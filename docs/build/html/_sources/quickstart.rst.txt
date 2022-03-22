Quickstart and Examples
=======================

The default environment is the best way to use the calculator. To get started, do one of the following
 - In the repository directory, run ``python -m symcalc``
 - Run ``interact.py``
 - Install the package and run ``import symcalc; symcalc.use()``

In the default environment, the calculator will understand normal mathmatical notation. 
 - Symbol definitions are not necessary. All unknown variables are assumed to be symbols.
 - Multiplication by juxtaposition is supported. ``2ab`` will be ``2*a*b``` if ``a`` is defined and ``ab`` is not. 
 - Numbers entered are exact: ``1.2`` is equivalent to ``6/5``

Examples
--------
.. code-block:: 

    Calculator >>> solve(x**2+4x-7)
    New symbol: x
    [-2 + √11, -√11 - 2]
    Decimals: [1.3166, -5.3166]
    Result stored in out[1]

    Calculator >>> solveset(sin(x))
    {2⋅n⋅π │ n ∊ ℤ} ∪ {2⋅n⋅π + π │ n ∊ ℤ}
    Result stored in out[2]

    Calculator >>> diff(2x**2sin(x))
      2
    2⋅x ⋅cos(x) + 4⋅x⋅sin(x)
    Result stored in out[3]

    Calculator >>> _.subs(x, 3)
    18⋅cos(3) + 12⋅sin(3)
    Decimal: -16.1264248420896
    Result stored in out[4]
    
    Calculator >>> integrate(sin(x)**2, (x,0,2))
      sin(2)⋅cos(2)
    - ───────────── + 1
            2
    Decimal: 1.18920062382698
    Result stored in out[5]

    Calculator >>> v[1,2,3]+v[4,5,6]
    ⎡5⎤
    ⎢ ⎥
    ⎢7⎥
    ⎢ ⎥
    ⎣9⎦
    Result stored in out[6]

    Calculator >>> m[1,2,3\\3,2,1\\5,5,9]
    ⎡1  2  3⎤
    ⎢       ⎥
    ⎢3  2  1⎥
    ⎢       ⎥
    ⎣5  5  9⎦
    Result stored in out[7]

    Calculator >>> _.det()
    -16
    Result stored in out[8]

    Calculator >>> out[7]*out[6]
    ⎡46 ⎤
    ⎢   ⎥
    ⎢38 ⎥
    ⎢   ⎥
    ⎣141⎦
    Result stored in out[9]

For a more thorough list of the calculator's capabilities, see :doc:`capabilities` or SymPy documentation.