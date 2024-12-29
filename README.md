# LetsGoGambling
# Chernoff-Hoeffding Inequality
$$
P(|S_n - p| < \epsilon) \geq 1 - 2 * \exp {\frac{-2 * n * \epsilon ^ 2}{(1.5 - (-1)) ^ 2}} \Leftrightarrow
$$
$$
\Leftrightarrow n > - \frac {\ln {\frac {1 - \alpha}{2}} * 6.25}{2 * \epsilon ^ 2} \approx 1153
$$
# Bet sizing
Since losing the bet means losing the entire wager, we use can use the following formula given by the Kelly criterion:

$$
f^* = p - \frac{p}{q}
$$

p is the probability of winning, q = 1 - p and b is the proportion of the bet gained for a win

In this case, we would have a random variable that looks like this:

$$
X  \ \textasciitilde \ 
\begin{pmatrix}
b & -1 \\
p & q
\end{pmatrix}
$$

$$
\text{And } f^* = \frac {E[X]}{b}
$$

But for a hand of blackjack it looks like this:

$$
X'  \ \textasciitilde \ 
\begin{pmatrix}
1 & 1.5 & 0 & -1 \\
w & j & t & q
\end{pmatrix}
$$

So the bet is equal to the expected value of the next game / payoff (can consider =1) 


