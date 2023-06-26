import numpy as np

from config import canvas_width, canvas_height, stripe_width

block_a = np.ones((stripe_width, stripe_width))
block_b = np.ones((stripe_width, stripe_width)) * 2

# https://www.perplexity.ai/search/c668a1fd-85ef-4bfc-a6a0-5a4ff9604d9d?s=c
stripe_mask_v = np.tile(np.hstack((block_a, block_b)), (400, 400))
stripe_mask_v = stripe_mask_v[:canvas_width, :canvas_height]

# Horizontal = rotated vertical mask
stripe_mask_h = stripe_mask_v.T

# To create a checkers pattern, combine horizontal and vertical pattern
# Intersection points and points where no lines meet should become "checked"
stripe_mask_c = stripe_mask_v * stripe_mask_h
stripe_mask_c = np.where(stripe_mask_c == 2, 2, 1)
