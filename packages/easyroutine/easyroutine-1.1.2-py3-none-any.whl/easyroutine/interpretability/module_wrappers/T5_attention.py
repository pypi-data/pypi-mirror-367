import torch
import torch.nn as nn
from typing import Optional, Tuple
from easyroutine.interpretability.module_wrappers.base import (
    BaseAttentionWrapper,
    AttentionMatrixHookModule,
)


class T5AttentionWrapper(BaseAttentionWrapper):
    @staticmethod
    def original_name() -> str:
        return "T5Attention"

    def __init__(self, original_attention: nn.Module):
        super().__init__(original_attention)
        self.q = original_attention.q
        self.k = original_attention.k
        self.v = original_attention.v
        self.o = original_attention.o
        self.dropout = original_attention.dropout
        self.layer_idx = original_attention.layer_idx
        self.n_heads = original_attention.n_heads
        self.key_value_proj_dim = original_attention.key_value_proj_dim
        self.inner_dim = original_attention.inner_dim
        self.has_relative_attention_bias = (
            original_attention.has_relative_attention_bias
        )
        self.pruned_heads = original_attention.pruned_heads
        self.attention_matrix_pre_softmax_hook = AttentionMatrixHookModule()
        self.attention_matrix_hook = AttentionMatrixHookModule()
        self.original_attention = original_attention

    def forward(
        self,
        hidden_states,
        mask=None,
        key_value_states=None,
        position_bias=None,
        past_key_value=None,
        layer_head_mask=None,
        query_length=None,
        use_cache=False,
        output_attentions=False,
        cache_position=None,
    ):
        """
        Self-attention (if key_value_states is None) or attention over source sentence (provided by key_value_states).
        """
        # Input is (batch_size, seq_length, dim)
        # Mask is (batch_size, 1, 1, key_length) (non-causal encoder) or (batch_size, 1, seq_length, key_length) (causal decoder)
        batch_size, seq_length = hidden_states.shape[:2]

        # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
        is_cross_attention = key_value_states is not None

        query_states = self.q(hidden_states)
        query_states = query_states.view(
            batch_size, -1, self.n_heads, self.key_value_proj_dim
        ).transpose(1, 2)

        if past_key_value is not None:
            is_updated = past_key_value.is_updated.get(self.layer_idx)
            if is_cross_attention:
                # after the first generated id, we can subsequently re-use all key/value_states from cache
                curr_past_key_value = past_key_value.cross_attention_cache
            else:
                curr_past_key_value = past_key_value.self_attention_cache

        current_states = key_value_states if is_cross_attention else hidden_states
        if is_cross_attention and past_key_value is not None and is_updated:  # type: ignore
            # reuse k,v, cross_attentions
            key_states = curr_past_key_value.key_cache[self.layer_idx]  # type: ignore
            value_states = curr_past_key_value.value_cache[self.layer_idx]  # type: ignore
        else:
            key_states = self.k(current_states)
            value_states = self.v(current_states)
            key_states = key_states.view(
                batch_size, -1, self.n_heads, self.key_value_proj_dim
            ).transpose(1, 2)
            value_states = value_states.view(
                batch_size, -1, self.n_heads, self.key_value_proj_dim
            ).transpose(1, 2)

            if past_key_value is not None:
                # save all key/value_states to cache to be re-used for fast auto-regressive generation
                cache_position = cache_position if not is_cross_attention else None
                key_states, value_states = curr_past_key_value.update(  # type: ignore
                    key_states,
                    value_states,
                    self.layer_idx,
                    {"cache_position": cache_position},
                )
                # set flag that curr layer for cross-attn is already updated so we can re-use in subsequent calls
                if is_cross_attention:
                    past_key_value.is_updated[self.layer_idx] = True

        # compute scores, equivalent of torch.einsum("bnqd,bnkd->bnqk", query_states, key_states), compatible with onnx op>9
        scores = torch.matmul(query_states, key_states.transpose(3, 2))

        if position_bias is None:
            key_length = key_states.shape[-2]
            # cache position is 0-indexed so we add 1 to get the real length of queries (aka with past)
            real_seq_length = (
                query_length if query_length is not None else cache_position[-1] + 1 # type: ignore
            )  # type: ignore
            if not self.has_relative_attention_bias:
                position_bias = torch.zeros(
                    (1, self.n_heads, seq_length, key_length),
                    device=scores.device,
                    dtype=scores.dtype,
                )
                if self.gradient_checkpointing and self.training:
                    position_bias.requires_grad = True
            else:
                position_bias = self.compute_bias(
                    real_seq_length,
                    key_length,
                    device=scores.device,
                    cache_position=cache_position,
                )
                position_bias = position_bias[:, :, -seq_length:, :]

            if mask is not None:
                causal_mask = mask[:, :, :, : key_states.shape[-2]]
                position_bias = position_bias + causal_mask

        if self.pruned_heads:
            mask = torch.ones(position_bias.shape[1])
            mask[list(self.pruned_heads)] = 0
            position_bias_masked = position_bias[:, mask.bool()]
        else:
            position_bias_masked = position_bias

        scores += position_bias_masked

        # (batch_size, n_heads, seq_length, key_length)
        attn_weights = self.attention_matrix_pre_softmax_hook(scores)
        attn_weights = nn.functional.softmax(scores.float(), dim=-1).type_as(scores)
        attn_weights = self.attention_matrix_hook(attn_weights)
        attn_weights = nn.functional.dropout(
            attn_weights, p=self.dropout, training=self.training
        )

        # Mask heads if we want to
        if layer_head_mask is not None:
            attn_weights = attn_weights * layer_head_mask

        attn_output = torch.matmul(attn_weights, value_states)

        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
        attn_output = self.o(attn_output)

        outputs = (attn_output, past_key_value, position_bias)

        if output_attentions:
            outputs = outputs + (attn_weights,)
        return outputs
