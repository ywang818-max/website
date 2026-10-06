# Blog 1: Lagrange multipliers

This is an explanatory article, not an empirical dataset analysis. The example uses U(x,y) = ln(x) + ln(y), positive x and y, prices 2 and 1, and income 100. The optimal bundle is (25,50), and the multiplier for L = U + lambda(M-2x-y) is 2/M = 0.02 utility units per dollar at M=100. Strict concavity makes the interior first-order conditions sufficient for this example. Changing the utility scale or constraint normalization changes the multiplier's numerical value.

`index.qmd` is the article. `code/figure.py` creates `lagrange-intuition.png` directly from the equations. No external data are used.

To regenerate the figure, install Python with numpy and matplotlib, then from the website root run:

```sh
python blog/posts/post1/code/figure.py
```

To render the article, run `quarto render blog/posts/post1/index.qmd` from the website root. The formal repository checklist begins with Blog 2; this supporting code is provided for transparency, not because Blog 1 requires a repository.
