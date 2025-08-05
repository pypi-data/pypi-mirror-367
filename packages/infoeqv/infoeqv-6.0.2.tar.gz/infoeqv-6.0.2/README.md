
---

## 🧠 Theory: Information Equivalent Designs in the Cubic Regression Model and the De La Garza Phenomenon

### 🔷 Introduction

In the theory of optimal experimental designs, the **De La Garza Phenomenon** refers to the striking result that, for polynomial regression models of degree $$p$$, any optimal design (with respect to the Loewner ordering of information matrices) can be replaced by a design with at most $$p + 1$$ support points. This significantly simplifies the search for optimal designs.

For a **cubic regression model**, this means that although one may start with a design involving many design points, an equivalent design with just **four support points** (or even fewer under special symmetry conditions) can exist and be **Loewner superior or equivalent** in terms of information content.

### 🔷 Cubic Regression Model

Consider the cubic polynomial regression model on the interval $$[-1, 1]$$:

$$
y = \beta_0 + \beta_1 x + \beta_2 x^2 + \beta_3 x^3 + \varepsilon
$$

where $$\varepsilon \sim N(0, \sigma^2)$$, and $$x \in [-1, 1]$$ is the design variable. For each design point $$x_i$$, the information matrix contribution is:

$$
f(x_i) f(x_i)^T \quad \text{where} \quad f(x_i) = [1, x_i, x_i^2, x_i^3]^T
$$

The overall information matrix of a design $$D_n = \{x_1, \dots, x_n; f_1, \dots, f_n\}$$ with frequencies $$f_i$$ is:

$$
M(D_n) = \sum_{i=1}^n f_i \cdot f(x_i) f(x_i)^T
$$

### 🔷 De La Garza Phenomenon for Cubic Models

According to the **De La Garza Phenomenon**, for a cubic model (degree 3), a design supported on **more than four points** can be **dominated in the Loewner order** by a **four-point design**, possibly symmetric, with equivalent or better information.

The **Loewner order** $$A \succeq B$$ means that $$A - B$$ is **positive semi-definite**, implying $$A$$ contains more or equal information than $$B$$.

### 🔷 Information Equivalent Design

An **Information Equivalent Design** is a reduced design (often with fewer support points) that matches the original design in key information metrics—typically the **moments** of the design.

For symmetric designs on $$[-1,1]$$, the **odd central moments vanish**, simplifying the comparison. The relevant **even-order central moments** are:

* $$\mu_2 = \frac{1}{n} \sum f_i x_i^2$$
* $$\mu_4 = \frac{1}{n} \sum f_i x_i^4$$
* $$\mu_6 = \frac{1}{n} \sum f_i x_i^6$$

These moments define the key entries of the **Fisher Information Matrix** for the cubic model.

### 🔷 Theorem: Two-Point Information Equivalent Design

**Given**:

* A symmetric design $$D_n$$ with $$n = 2k$$ total frequency.
* Known second-order moment $$\mu_2'$$.
* You seek a 2-point symmetric design $$D_4^*$$ of the form:

\[$$D_4^*=\left\{(\pm a^*,\frac{n-2f}{2}),(\pm b^*,f)\right\},\quad-1\leq a^*<b^*\leq 1$$\]


**Then**, under the following conditions:

1. $$k(1 - \mu_2') < f < k$$
2. $$f b^{*2} < k \mu_2'$$ and $$\mu_2' < b^{*2} < 1$$
3. $$f \mu_2'^3 \geq k \mu_6'$$

there **exists** such a design $$D_4^*$$ that is **information equivalent** to $$D_n$$ and satisfies:

* $$\text{Moment 2 (quadratic):} \quad (n - 2f)a^2 + 2f b^2 = n \mu_2'$$
* $$\text{Moment 4 (quartic):} \quad (n - 2f)a^4 + 2f b^4 = n \mu_4'$$
* $$\text{Moment 6 (sextic):} \quad (n - 2f)a^6 + 2f b^6 = n \mu_6'$$

Thus, this **two-point design dominates** the original multivariate design in the **Loewner order** of information matrices.

### 🔷 Significance

* Simplifies implementation in real-world designs: only two support points needed.
* Shows that information redundancy exists in symmetric high-point designs.
* Key in **computational efficiency** and in theoretical understanding of **optimal design spaces**.

### 🔷 Applications

* **Engineering experiments** involving polynomial approximations.
* **Cricket pitch analysis** (predicting ball trajectory).
* **Educational psychology**, e.g., modeling learning curves.
* **Agriculture**, especially in response surface methodology for input-output modeling.


## 🧠 About the Package `infoeqv`

The Python package **`infoeqv`** implements the construction of **Information Equivalent Designs** for the **cubic regression model**, based on a theoretical result that simplifies `n`-point symmetric designs into 2- or 4-point designs, often achieving equal or better statistical efficiency. This is aligned with the classical **De La Garza phenomenon**, which states that under certain regression models, optimal designs use fewer support points.

The core utility of the package is to automate the process of:

* Validating a given symmetric design (user-defined `x` and `f`)
* Computing information equivalent **two-point designs**
* Checking if these designs satisfy moment-matching conditions and **Loewner domination**
* Displaying results graphically and numerically

This tool can be useful for **statisticians, engineers, data scientists**, and researchers working in **optimal experimental design** or **regression modeling**.

---

## 🔧 Core Function: `info_eqv_design(x, f)`

This is the **main function** exported by the `infoeqv` package. It accepts two arguments:

* `x`: A 1D list or array of symmetric design points in the interval `[-1, 1]`
* `f`: A 1D list or array of their corresponding frequencies (must be even in total)

```python
from infoeqv import info_eqv_design

x = [-0.8, -0.4, 0.4, 0.8]
f = [4, 3, 3, 4]

info_eqv_design(x, f)
```

When executed, this function:

1. **Validates input** to ensure symmetry and proper frequency format.
2. **Standardizes** design for analysis within the symmetric interval.
3. **Computes moments** μ₂′, μ₄′, μ₆′.
4. Iteratively searches for valid **two-point information equivalent designs** `(±a*, ±b*)` using the theoretical formulas.
5. For each design, checks:

   * Condition (i): Second moment feasibility and bounds on `f`
   * Condition (ii): Bounds on `b²`
   * Condition (iii): Sixth moment inequality (dominance)
6. **Displays output**:

   * A table summarizing valid/invalid design points
   * A graph showing the conditions met by each candidate

---

## 🧪 How the Theory Was Translated into Code

The theoretical foundations involve solving three nonlinear moment equations (second, fourth, and sixth) under symmetry, and checking if the reduced design dominates the original in the **Loewner sense**. The following components were used:

### 🧩 Algorithmic Implementation (Step-by-step):

* **Moment Equations**
  Using frequency-weighted formulas, the code computes:

  * $$μ₂′ = E\[X²], μ₄′ = E\[X⁴], μ₆′ = E\[X⁶]$$

* **Candidate Search**
  Iterate over possible `f` values (using `ceil`, `floor`) that satisfy:

  * $$k(1 - \mu_2') < f < k$$
  * $$fb^{*2} < k\mu_2'$$
  * $$\mu_2' < b^{*2} < 1$$

* **Design Construction**
  Using:

  $$
  a^* = \pm \sqrt{\frac{k\mu_2' - f b^{*2}}{k - f}}
  $$

  where $$a < b \in [-1, 1]$$

* **Verification**
  Each candidate is checked against:

  (i) Lower and upper bounds for `f`
  (ii) Condition on `b²` range
  (iii) $$f \mu_2'^3 \geq k \mu_6'$$

* **Plotting**
  Matplotlib is used to visually indicate which candidates satisfy each subset of the theorem's conditions.

---

## 📦 Installation Instructions

You can install the `infoeqv` package via pip once it is published to PyPI (or install directly from a local folder for testing):

### 🔹 Option 1: From PyPI (after publishing)

```bash
pip install infoeqv
```

### 🔹 Option 2: From a Local Folder

If you're still testing the package locally:

```bash
pip install .
```
## 🛠️ Usage Example

Once installed, you can use the function `info_eqv_design()` to analyze a symmetric design:

```python
# Example: symmetric cubic regression design with even frequency
import numpy as np
from infoeqv import info_eqv_design
x = [-1.5, -1, -0.5, 0, 0.5, 1, 1.5]
f = [2, 3, 5, 6, 5, 3, 2]
info_eqv_design(x, f)
```
```python
Original x values: [-1.5 -1.  -0.5  0.   0.5  1.   1.5]
Frequency f values: [2. 3. 5. 6. 5. 3. 2.]

Total number of observations (N): 26.0
Mean of x (x̄): 0.0000
Standardized values (d): [-1.     -0.6667 -0.3333  0.      0.3333  0.6667  1.    ]

Weighted mean (μ₁): 0.0000
Weighted second moment (μ₂): 0.2991
Central moment (μ₂₂): 0.2991
μ₆: 0.1746

Bounds: L = 5.9868, U = 20.0132
Ceiling of L (S): 6, Floor of U (T): 20

✅ Designs satisfying (i) & (ii), but failing ❌ (iii):
  n1   n2         d1         d2  Status
  14   12    -0.5064     0.5908   ❌ (iii)
  15   11    -0.4684     0.6387   ❌ (iii)
  16   10    -0.4324     0.6918   ❌ (iii)

```

![Output Plot or Graph](Figure_1.png)

This will output:

* The values of moments μ₂′, μ₄′, μ₆′
* A table of possible (a\*, b\*) values and corresponding `n1`, `n2` allocations
* Conditions satisfied for each case
* A graph showing which points satisfy conditions (i), (ii), and (iii)

---

## 🧪 Dependencies

Make sure the following libraries are available (they’ll be installed automatically if using `pip install`):

* `numpy`
* `matplotlib`
* `pandas`

---

## 👤 Author

**Rohit Kumar Behera**
📍 Odisha, India
📧 \rohitmbl24@gmail.com
🧪 Statistical Python Developer

This package and algorithm were created based on original theoretical research on **Information Equivalent Designs** for cubic regression models and implemented as a Python package `infoeqv`. The package can be used as a research tool, teaching aid, or practical software for statisticians and data scientists.

---
