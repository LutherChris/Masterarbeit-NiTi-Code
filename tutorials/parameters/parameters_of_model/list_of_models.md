# Models in Cartesian Coordinates

## model_regular_1

$$\begin{align*} f(x,y,z)= \sum_{i+j+k \le p} a_{ijk} \cdot x^{i}y^{j}z^{k} \end{align*}$$

- Simple polynomials in $x, y, z$
- In code: `p=p_order`
- `no_a0=True`: starting index = 1 (no $a_{0}$)
- Example ($p = 2$): $f(x,y,z)= a_{0}+a_{1}z+a_{2}y+a_{3}x+a_{4}z^{2}+a_{5}yz+a_{6}y^{2}+a_{7}xz+a_{8}xy+a_{9}x^{2}$

## model_regular_2

$$\begin{align*} f(x,y,z)= \sum_{i=0}^{p} \sum_{j=0}^{p} \sum_{k=0}^{p} a_{i,j,k} \cdot T_{i}(x) T_{j}(y) T_{k}(z) \end{align*}$$

- $T_{i}(x)$ are Chebyshev polynomials of the first kind
- In code: `p=p_order`
- `no_a0=True`: starting indices: $i=j=k = 1$

## model_regular_3

$$\begin{align*} f(x,y,z)=\sum_{i=0}^{p} \sum_{j=0}^{p} \sum_{k=0}^{p} a_{i,j,k} \cdot P_{i}(x) P_{j}(y) P_{k}(z) \end{align*}$$

- $P_{i}(x)$ are Legendre polynomials
- In code: `p=p_order`
- `no_a0=True`: starting indices: $i=j=k = 1$

## model_regular_4

$$f(x,y,z) = \sum_{i+j+k \le p} a_{ijk} \cdot x^{i}y^{j}z^{k} + \sum_{n=1}^{f} \sum_{\alpha, \beta, \gamma \in \{\sin,\cos\}} b_{n,\alpha \beta \gamma} \cdot \alpha(sknx) \beta(skny) \gamma(sknz)$$

- First part: simple polynomials in $x, y, z$
- Second part is a Fourier expansion consisting of 8 combinations of sine and cosine:

$$\begin{align*} \sum_{n=1}^{f} ( & b_{n,1}\cos(\phi_{x})\cos(\phi_{y})\cos(\phi_{z}) + b_{n,2}\cos(\phi_{x})\cos(\phi_{y})\sin(\phi_{z}) \\ + & b_{n,3}\cos(\phi_{x})\sin(\phi_{y})\cos(\phi_{z}) + b_{n,4}\sin(\phi_{x})\cos(\phi_{y})\cos(\phi_{z}) \\ + & b_{n,5}\cos(\phi_{x})\sin(\phi_{y})\sin(\phi_{z}) + b_{n,6}\sin(\phi_{x})\cos(\phi_{y})\sin(\phi_{z}) \\ + & b_{n,7}\sin(\phi_{x})\sin(\phi_{y})\cos(\phi_{z}) + b_{n,8}\sin(\phi_{x})\sin(\phi_{y})\sin(\phi_{z}) ) \end{align*}$$

- $s$ = symmetry factor
- $k = \frac{2\pi}{L}$ = wavenumber
- $L$ = width of the cubic grid; for a grid scaled to $[-1,1]$, $L=2$
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting indices: $i=j=k = 1$

## model_regular_5

$$f(x,y,z) = \sum_{i+j+k \le p} a_{ijk} \cdot x^{i}y^{j}z^{k} + \sum_{n=1}^{f} \left[ \alpha_{n}\cdot \cos(skn(x+y+z)) + \beta_{n} \cdot \sin(skn(x+y+z)) \right]$$

- First part: simple polynomials in $x, y, z$
- Second part: Fourier expansion along the diagonal $x+y+z$
- $s$ = symmetry factor
- $k = \frac{2\pi}{L}$ = wavenumber
- $L$ = width of the cubic grid; for a grid scaled to $[-1,1]$, $L=2$
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting indices: $i=j=k = 1$

## model_regular_6

$$f(x,y,z) = \sum_{i+j+k \le p} a_{ijk} \cdot x^{i}y^{j}z^{k} + \sum_{a+b+c \le l} \sum_{n=1}^{f} \sum_{\alpha, \beta, \gamma \in \{\sin,\cos\}} b_{abc,n,\alpha \beta \gamma} \cdot x^{a}y^{b}z^{c}\alpha(sknx) \beta(skny) \gamma(sknz)$$

- `model_regular_4` $\subset$ `model_regular_6`
- First part: polynomial part
- Second part: product of polynomial part and Fourier part
- $s$ = symmetry factor
- $k = \frac{2\pi}{L}$ = wavenumber
- $L$ = width of the cubic grid; for a grid scaled to $[-1,1]$, $L=2$
- In code: `p=p_order`, `f=f_order`, `l=l_order`
- `no_a0=True`: starting indices: $i=j=k = 1$

## model_regular_7

$$\begin{align*} f(x,y,z) & = \sum_{i+j+k \le p} a_{ijk} \cdot x^{i}y^{j}z^{k} \\ &+ \sum_{a+b+c \le l} ~ \sum_{n=1}^{f} \left[ \alpha_{abc,n}\cdot x^{a}y^{b}z^{c} \cos(skn(x+y+z)) + \beta_{abc,n} \cdot x^{a}y^{b}z^{c} \sin(skn(x+y+z)) \right] \end{align*}$$

- `model_regular_5` $\subset$ `model_regular_7`
- First part: polynomial part
- Second part: product of polynomial part and Fourier part
- $s$ = symmetry factor
- $k = \frac{2\pi}{L}$ = wavenumber
- $L$ = width of the cubic grid; for a grid scaled to $[-1,1]$, $L=2$
- In code: `p=p_order`, `f=f_order`, `l=l_order`
- `no_a0=True`: starting indices: $i=j=k = 1$

# Models in Cylindrical Coordinates

## model_cylindrical_1

$$f(r,\phi,z)=\sum_{i+j \le p} a_{ij} \cdot r^{i}z^{j} + \sum_{n=1}^{f}\left[ \alpha_{n} \cdot \cos(sn\phi) + \beta_{n} \cdot \sin(sn\phi) \right]$$

- First term: polynomials in $r$ and $z$
- Second term: Fourier terms in $\phi$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting indices: $i=j = 1$

## model_cylindrical_2

$$f(r,\phi,z)=\sum_{i+j \le p} a_{ij} \cdot r^{i}z^{j} + \sum_{n=1}^{f} b_{n} \cdot r^{2n} \cos(sn\phi)$$

- First term: polynomials in $r$ and $z$
- Second term: product of even powers of polynomials and cosine functions
- All Fourier terms vanish at the origin $r=0$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting indices: $i=j = 1$

## model_cylindrical_3

$$f(r,\phi,z)=\sum_{i+j \le p} a_{ij} \cdot r^{i}z^{j} + \sum_{n=1}^{f} \left[ a_{n}\cdot r^{n}\cos(sn\phi) + b_{n}\cdot r^{n}\sin(sn\phi) + c_{n}\cdot z^{n}\cos(sn\phi) + d_{n}\cdot z^{n} \sin(sn\phi) \right]$$

- First term: polynomials in $r$ and $z$
- Second term: products of angular terms with polynomials in $r$ or $z$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting indices: $i=j = 1$

## model_cylindrical_4

$$f(r,\phi,z)= \sum_{i+j \le p} a_{ij} \cdot r^{i}z^{j} + \sum_{a+b \le l}~\sum_{n=1}^{f} \left[ \alpha_{ab,n} \cdot r^{a}z^{b} \cos(sn\phi) + \beta_{ab,n} \cdot r^{a}z^{b} \sin(sn\phi) \right]$$

- First term: polynomials in $r$ and $z$
- Second term: products of angular terms with polynomials in $r$ and $z$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`, `l=l_order`
- `no_a0=True`: starting indices: $i=j=a=b = 1$

# Models in Spherical Coordinates

## model_spherical_1

$$f(r,\theta,\phi) = \sum_{k=0}^{p}a_{k}\cdot r^{k} + \sum_{n=1}^{f} \left[ a_{n} \cdot \cos(sn\theta) + b_{n} \cdot \sin(sn\theta) + c_{n} \cdot \cos(sn\phi) + d_{n} \cdot \sin(sn\phi) \right]$$

- First term: radial term
- Second term: angular terms in $\theta$ and $\phi$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting index: $k = 1$

## model_spherical_2

$$f(r,\theta,\phi) = \sum_{k=0}^{p} a_{k} \cdot r^{k} + \sum_{m=0}^{l}~\sum_{n=1}^{f} \left[ a_{m,n} \cdot r^{m}\cos(sn\theta) + b_{m,n} \cdot r^{m}\sin(sn\theta) + c_{m,n}\cdot r^{m}\cos(sn\phi) + d_{m,n}\cdot r^{m}\sin(sn\phi) \right]$$

- First term: radial term
- Second term: angular terms in $\theta$ and $\phi$ multiplied by radial terms
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`, `l=l_order`
- `no_a0=True`: starting indices: $k=m = 1$

## model_spherical_3

$$f(r,\theta, \phi) = \sum_{k=0}^{p}~\sum_{l=0}^{L}~\sum_{m=-l}^{l} a_{klm}\cdot r^{k}Y_{l}^{m}(\theta,\phi)$$

- Real spherical harmonics $Y_{l}^{m}(\theta,\phi)$ multiplied by polynomial in $r$
- In code: `p=p_order`, `L=l_order`
- `no_a0=True`: starting index: $k = 1$

## model_spherical_4

$$f(r,\theta, \phi) = \sum_{k=0}^{p}~\sum_{l=0}^{L}~\sum_{m=-l}^{l} a_{klm}\cdot L_{k}Y_{l}^{m}(\theta,\phi)$$

- Real spherical harmonics $Y_{l}^{m}(\theta,\phi)$ multiplied by radial basis of Laguerre polynomials
- In code: `p=p_order`, `L=l_order`
- `no_a0=True`: starting index: $k = 1$

# Special Models with Coordinate Transformation for Point 1 in Cartesian Coordinates

## model_point1_xyz_1

$$f(x,y,z) = \sum_{k=0}^{p}~\sum_{m=0}^{f} a_{km}\cdot (r')^{k} |z-z_{0}|^{m} + \sum_{n=0}^{l}b_{n} \cdot|z|^{n}$$

where:

$$r'= \sqrt{(x-x_{0})^{2} + (y-y_{0})^{2} + (z-z_{0})^{2}}$$

with

$$\vec{r}(t)=\left(\begin{array}{c} x \\ a_{1}x+a_{2}x^{2}+a_{3}x^{3}+a_{4}x^{4} \\ b_{1}x + b_{2}x^{2}+ b_{3}x^{3} + b_{4}x^{4} \end{array}\right)=\left(\begin{array}{c} x_{0} \\ y_{0} \\ z_{0} \end{array}\right)$$

with

|       | coeffs_x | coeffs_y            | coeffs_z            |
| ----- | -------- | ------------------- | ------------------- |
| $a_0$ |          |                     |                     |
| $a_1$ |          | -0.7332429642612501 | -0.7332557473726407 |
| $a_2$ |          | 1.7826111869586354  | 1.7698517082611422  |
| $a_3$ |          | -8.391775184580466  | -8.400680635383303  |
| $a_4$ |          | 99.06024644165981   | 222.30588634644334  |

- In code: `p=p_order`, `f=f_order`, `l=l_order`

## model_point1_xyz_2

$$f(x,y,z) = \sum_{n=0}^{5} a_{n} \cdot r' |z|^{n} + a_{7} \cdot z + a_{8} \cdot |z|$$

- Function was used to test options manually. Optionally replaced:
	- $r \leftrightarrow r'$
	- $(z-z_0) \leftrightarrow z$

where:

$$r'= \sqrt{(x-x_{0})^{2} + (y-y_{0})^{2} + (z-z_{0})^{2}}$$

with

$$\vec{r}(t)=\left(\begin{array}{c} x \\ a_{1}x+a_{2}x^2 \\ b_{2}x^2 \end{array}\right)=\left(\begin{array}{c} x_{0} \\ y_{0} \\ z_{0} \end{array}\right)$$

with $a_{1}=-0.35993031 \quad a_{2}=0.29889326 \quad b_{2}= 0.93519459$ (from the initial rough path calculation)

# Path Functions

## model_path_1

$$f(t,\rho,\phi) = \sum_{k=0}^{p}~\sum_{n=1}^{f} \rho^{k} \left[ a_{kn}\cdot \sin(sn\phi) + b_{kn} \cdot \cos(sn\phi) \right]$$

- No $t$-dependence
- Polynomial in $\rho$
- Fourier expansion in $\phi$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`
- `no_a0=True`: starting index: $k = 1$

## model_path_2

$$f(t,\rho,\phi) = \sum_{m=0}^{l}c_{m}t^{m} + \sum_{m=0}^{l}~ \sum_{k=0}^{p}~\sum_{n=1}^{f} t^{m} \rho^{k} \left[ a_{kn}\cdot \sin(sn\phi) + b_{kn} \cdot \cos(sn\phi) \right]$$

- Polynomial in $t$
- Polynomial in $\rho$
- Fourier expansion in $\phi$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`, `l=l_order`
- `no_a0=True`: starting indices: $k = 1, m=1$

## model_path_3

$$f(t,\rho,\phi) = \sum_{k=0}^{p}~\sum_{m=1}^{f} a_{km} \cdot \rho^{k} \sin(sm\phi) + \sum_{k=0}^{p}~\sum_{n=1}^{l} b_{kn} \cdot \rho^{k} \cos(sn\phi)$$

- Like `model_path_1`, except sine and cosine terms have different maximum orders
- No $t$-dependence
- Polynomial in $\rho$
- Separate Fourier expansion in $\phi$
- $s$ = symmetry factor
- In code: `p=p_order`, `f=f_order`, `l=l_order`
- `no_a0=True`: starting index: $k = 1$

## model_path_4

$$f(t,\rho,\phi) = \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{m=1}^{f} a_{ijm} \cdot t^{i} \rho^{j} \sin(sm\phi) + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=1}^{l} b_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi)$$

- Like `model_path_3`, but full tensor product with $t$-dependence
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=1$)
- Separate Fourier expansion in $\phi$
- In code: `p=p_order`, `f=f_order`, `l=l_order`, `k=k_order`

## model_path_5

$$f(t,\rho,\phi) = \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=1}^{l} a_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi)$$

- Like `model_path_4`, but without sine components
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=1$)
- Pure cosine Fourier series
- In code: `p=p_order`, `l=l_order`, `k=k_order`

## model_path_6

$$f(t,\rho,\phi) = \sum_{k=1}^{p}~\sum_{m=1}^{f} a_{km} \cdot \rho^{k} \sin(sm\phi) + \sum_{k=1}^{p}~\sum_{n=1}^{l} b_{kn} \cdot \rho^{k} \cos(sn\phi)$$

- Restricted special case of `model_path_3`
- `model_path_6` is identical to `model_path_3` when `no_a0=True`
- Order in $\rho$ starts at 1
- In code: `p=p_order`, `l=l_order`, `k=k_order`

# Path Functions with Absolute Value Functions for Point 1

## model_path_abs_1

$$f(t,\rho,\phi) = \sum_{i=0}^{k}~\sum_{j=1}^{p} a_{ij} \cdot t^{i} \rho^{j} |\sin(s\phi)| + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{m=1}^{f} b_{ijm} \cdot t^{i} \rho^{j} \sin(sm\phi) + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=1}^{l} c_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi)$$



- Extension of `model_path_4` by an $|\sin|$ term
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=1$)
- Separate Fourier expansion in $\phi$
- Non-smooth basis term $|\sin(s\phi)|$
- Non-differentiable at $\phi=n\pi$
- In code: `p=p_order`, `f=f_order`, `l=l_order`, `k=k_order`

## model_path_abs_2

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=1}^{p} a_{ij} \cdot t^{i} \rho^{j} |\sin(\phi)| + \sum_{i=0}^{k}~\sum_{j=1}^{p} b_{ij} \cdot t^{i} \rho^{j} |\cos(\phi)| \\& + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{m=1}^{f} c_{ijm} \cdot t^{i} \rho^{j} \sin(sm\phi) + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=1}^{l} d_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Generalization of `model_path_abs_1` by $|\cos|$ terms
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=1$)
- Separate Fourier expansion in $\phi$
- Non-smooth $|\sin(\phi)|$ and $|\cos(\phi)|$ terms
- Non-differentiable at $\phi=0,\frac{\pi}{2}, \pi, \dots$
- No symmetry factor in the absolute value terms
- In code: `p=p_order`, `f=f_order`, `l=l_order`, `k=k_order`

## model_path_abs_3

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=0}^{p} a_{ij} \cdot t^{i} \rho^{j} |\sin(\phi)| + \sum_{i=0}^{k}~\sum_{j=0}^{p} b_{ij} \cdot t^{i} \rho^{j} |\cos(\phi)| \\& + \sum_{i=0}^{k}~\sum_{j=0}^{p}~\sum_{m=1}^{f} c_{ijm} \cdot t^{i} \rho^{j} \sin(sm\phi) + \sum_{i=0}^{k}~\sum_{j=0}^{p}~\sum_{n=1}^{l} d_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Identical to `model_path_abs_2`, except orders $\rho^{0}$ are permitted

## model_path_abs_4

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=1}^{p} a_{ij} \cdot t^{i} \rho^{j} \sqrt{\sin^{2}(\phi)+\epsilon}~ + \sum_{i=0}^{k}~\sum_{j=1}^{p} b_{ij} \cdot t^{i} \rho^{j} \sqrt{\cos^{2}(\phi) + \epsilon} \\& + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{m=1}^{f} c_{ijm} \cdot t^{i} \rho^{j} \sin(sm\phi) + \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=1}^{l} d_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Identical to `model_path_abs_3`, with the difference:
  The absolute value functions in $|\sin(\phi)|$ and $|\cos(\phi)|$ were smoothed by:

$$|\sin(\phi)| \rightarrow \sqrt{\sin^{2}(\phi)+\epsilon},\quad |\cos(\phi)| \rightarrow \sqrt{\cos^{2}(\phi) + \epsilon}$$

- $\epsilon$ controls how strongly the cusps of the absolute value functions are rounded
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=1$)
- Separate Fourier expansion in $\phi$
- No symmetry factor in the absolute value terms
- In code: `p=p_order`, `f=f_order`, `l=l_order`, `k=k_order`

## model_path_abs_5

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=0}^{p} a_{ij} \cdot t^{i} \rho^{j} \sqrt{\sin^{2}(\phi)+\epsilon}~ + \sum_{i=0}^{k}~\sum_{j=0}^{p} b_{ij} \cdot t^{i} \rho^{j} \sqrt{\cos^{2}(\phi) + \epsilon} \\& + \sum_{i=0}^{k}~\sum_{j=0}^{p}~\sum_{m=1}^{f} c_{ijm} \cdot t^{i} \rho^{j} \sin(sm\phi) + \sum_{i=0}^{k}~\sum_{j=0}^{p}~\sum_{n=1}^{l} d_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Like `model_path_abs_4`, but with allowed order $p=0$

# Models for Point 2

## model_path_point2_1

$$f(t,\rho,\phi)= \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{j_{1}=1}^{p_{1}}~\sum_{j_{2}=1}^{p_{2}}~\sum_{j_{3}=1}^{p_{3}} a_{ijj_{1}j_{2}j_{3}} \cdot t^{i} \rho^{j} \chi_{1}^{j_{1}} \chi_{2}^{j_{2}} \chi_{3}^{j_{3}}$$

where

$$\chi_{i}(t)=\sqrt{(x-x_{\min,i}(t))^{2} + (y-y_{\min,i}(t))^{2} + (z-z_{\min,i}(t))^{2}}$$

- $x_{\min,i}, y_{\min,i}, z_{\min,i}$ are the coordinates of the points on path 2B, $i=1,2,3$.
- $\chi_{i}$ are therefore the distances to path 2A
- Tensor product of polynomials in $\rho$, $t$, and $\chi_{i}$
- Starting point in $t$: order 0
- Starting point in all other polynomials: order 1
- No symmetry factor $s$
- In code: `p=p_order`, `k=k_order`, `p1=p1_order`, `p2=p2_order`, `p3=p3_order`

## model_path_point2_2

$$f(t,\rho,\phi)=\sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{j_{1}=0}^{p_{1}} a_{ijj_{1}} \cdot t^{i} \rho^{j} \chi_{1}^{j_{1}}$$

where

$$\chi_{1}(t)=\sqrt{\rho^{2}+\rho_{\min}^{2}(t)-2\rho\rho_{\min}(t)\cos(s\phi) +\epsilon}$$

- $\rho_{\min}$ is the radius of Point 2B as a function of $t$
- $\epsilon = 10^{-8}$ ensures numerical stability
- Improves `model_path_point1` by exploiting symmetry
- $s$ = symmetry factor
- Starting point in $t$: order 0
- Starting point in all other polynomials: order 1
- In code: `p=p_order`, `k=k_order`, `p1=p1_order`

## model_path_point2_3

$$f(t,\rho,\phi)=\sum_{i=0}^{k}~\sum_{j=0}^{p}~\sum_{j_{0}=0}^{p_{1}} a_{ijj_{1}} \cdot t^{i} \rho^{j} \chi_{1}^{j_{1}}$$

where

$$\chi_{1}(t)=\sqrt{\rho^{2}+\rho_{\min}^{2}(t)-2\rho\rho_{\min}(t)\cos(s\phi) +\epsilon}$$

- Identical to `model_path_point2_2`, with the difference that 0th orders in $\rho$ and $\chi_{1}$ are allowed
- In code: `p=p_order`, `k=k_order`, `p1=p1_order`

# Models for Point 3

## model_path_point3_1

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=1}^{p} b_{ij} \cdot t^{i} \rho^{j} \sqrt{\cos^{2}(\phi) + \epsilon} +  \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=1}^{l} d_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Like `model_path_abs_4`, but without sine components

## model_path_point3_2

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=0}^{l} a_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Identical to `model_path_5`, except $n=0$ instead of $n=1$ (allows angle-independent terms)
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=1$)
- Pure cosine Fourier series
- In code: `p=p_order`, `l=l_order`, `k=k_order`

## model_path_point3_3

$$\begin{align*} f(t,\rho,\phi) & = \sum_{i=0}^{k}~\sum_{j=1}^{p}~\sum_{n=0}^{l} a_{ijn} \cdot t^{i} \rho^{j} \cos(sn\phi) \end{align*}$$

- Identical to `model_path_point3_2`, with the difference that $\rho=0$ is allowed (enables shift of band energies via a constant part)
- Polynomial in $t$ (starting at $k=0$)
- Polynomial in $\rho$ (starting at $\rho=0$)
- Pure cosine Fourier series
- In code: `p=p_order`, `l=l_order`, `k=k_order`