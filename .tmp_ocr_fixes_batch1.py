FIXES = {
  "4e18fc5d": {
    "prompt": "v = -w/(150x)\nThe given equation relates the distinct positive numbers v, w, and x. Which equation correctly expresses w in terms of v and x?",
    "choices": [
      {"text": "w = -150vx"},
      {"text": "w = -150v/x"},
      {"text": "w = -x/(150v)"},
      {"text": "w = v + 150x"},
    ],
    "answer": 0,
    "equations": [],
    "explanation": (
      "Choice A is correct. It's given that x is positive. Therefore, multiplying each side of the given equation by -150x yields -150xv = w, which is "
      "equivalent to w = -150vx. Thus, the equation w = -150vx correctly expresses w in terms of v and x.\n"
      "\n"
      "Choice B is incorrect. This equation is equivalent to v = -wx/150.\n"
      "\n"
      "Choice C is incorrect. This equation is equivalent to v = -x/(150w).\n"
      "\n"
      "Choice D is incorrect. This equation is equivalent to v = w - 150x."
    ),
  },
  "f5c3e3b8": {
    "prompt": "Which expression is equivalent to (m^4 q^4 z^(-1))(m q^5 z^3), where m, q, and z are positive?",
    "choices": [
      {"text": "m^4 q^20 z^(-3)"},
      {"text": "m^5 q^9 z^2"},
      {"text": "m^6 q^8 z^(-1)"},
      {"text": "m^20 q^12 z^(-2)"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. Applying the commutative property of multiplication, the expression (m^4 q^4 z^(-1))(m q^5 z^3) can be rewritten as "
      "(m^4 m)(q^4 q^5)(z^(-1) z^3). For positive values of x, (x^a)(x^b) = x^(a+b). Therefore, the expression (m^4 m)(q^4 q^5)(z^(-1) z^3) can be rewritten as "
      "(m^(4+1))(q^(4+5))(z^(-1+3)), or m^5 q^9 z^2.\n"
      "\n"
      "Choice A is incorrect and may result from multiplying, not adding, the exponents.\n"
      "\n"
      "Choice C is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
  },
  "3c95093c": {
    "prompt": "6x - 9y > 12\nWhich of the following inequalities is equivalent to the inequality above?",
    "choices": [
      {"text": "x - y > 2"},
      {"text": "2x - 3y > 4"},
      {"text": "3x - 2y > 4"},
      {"text": "3y - 2x > 2"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. Both sides of the given inequality can be divided by 3 to yield 2x - 3y > 4.\n"
      "\n"
      "Choices A, C, and D are incorrect because they are not equivalent to (do not have the same solution set as) the given inequality. For example, the "
      "ordered pair (0, -1.5) is a solution to the given inequality, but it is not a solution to any of the inequalities in choices A, C, or D."
    ),
  },
  "dd4ab4c4": {
    "prompt": "4a^2 + 20ab + 25b^2\nWhich of the following is a factor of the polynomial above?",
    "choices": [
      {"text": "a + b"},
      {"text": "2a + 5b"},
      {"text": "4a + 5b"},
      {"text": "4a + 25b"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. The first and last terms of the polynomial are both squares such that 4a^2 = (2a)^2 and 25b^2 = (5b)^2. The second term "
      "is twice the product of the square root of the first and last terms: 20ab = 2(2a)(5b). Therefore, the polynomial is the square of a binomial "
      "such that 4a^2 + 20ab + 25b^2 = (2a + 5b)^2, and (2a + 5b) is a factor.\n"
      "\n"
      "Choice A is incorrect and may be the result of incorrectly factoring the polynomial.\n"
      "\n"
      "Choice C is incorrect and may be the result of dividing the second and third terms of the polynomial by their greatest common factor.\n"
      "\n"
      "Choice D is incorrect and may be the result of not factoring the coefficients."
    ),
  },
  "b8caaf84": {
    "prompt": "If p = 3x + 4 and v = x + 5, which of the following is equivalent to pv - 2p + v?",
    "choices": [
      {"text": "3x^2 + 12x + 7"},
      {"text": "3x^2 + 14x + 17"},
      {"text": "3x^2 + 19x + 20"},
      {"text": "3x^2 + 26x + 33"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. It's given that p = 3x + 4 and v = x + 5. Substituting the values for p and v into the expression pv - 2p + v yields "
      "(3x + 4)(x + 5) - 2(3x + 4) + x + 5. Multiplying the terms (3x + 4)(x + 5) yields 3x^2 + 4x + 15x + 20. Using the distributive "
      "property to rewrite -2(3x + 4) yields -6x - 8. Therefore, the entire expression can be represented as "
      "3x^2 + 4x + 15x + 20 - 6x - 8 + x + 5. Combining like terms yields 3x^2 + 14x + 17.\n"
      "\n"
      "Choice A is incorrect and may result from subtracting, instead of adding, the term x + 5.\n"
      "\n"
      "Choice C is incorrect. This is the result of multiplying the terms (3x + 4)(x + 5).\n"
      "\n"
      "Choice D is incorrect and may result from distributing 2, instead of -2, to the term 3x + 4."
    ),
  },
  "7f81d0c3": {
    "prompt": "x^2 - x - 1 = 0\nWhat values satisfy the equation above?",
    "choices": [
      {"text": "x = 1 and x = 2"},
      {"text": "x = -1/2 and x = 3/2"},
      {"text": "x = (1 + √5)/2 and x = (1 - √5)/2"},
      {"text": "x = (-1 + √5)/2 and x = (-1 - √5)/2"},
    ],
    "answer": 2,
    "equations": [],
    "explanation": (
      "Choice C is correct. Using the quadratic formula to solve the given expression yields "
      "x = (-(-1) ± √((-1)^2 - (4)(1)(-1)))/((2)(1)) = (1 ± √5)/2. "
      "Therefore, x = (1 + √5)/2 and x = (1 - √5)/2 satisfy the given equation.\n"
      "\n"
      "Choices A and B are incorrect and may result from incorrectly factoring or incorrectly applying the quadratic formula.\n"
      "\n"
      "Choice D is incorrect and may result from a sign error."
    ),
  },
  "e312081b": {
    "prompt": "(x + 5) + (2x - 3)\nWhich of the following is equivalent to the given expression?",
    "choices": [
      {"text": "3x - 2"},
      {"text": "3x + 2"},
      {"text": "3x - 8"},
      {"text": "3x + 8"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. Using the associative and commutative properties of addition, the given expression (x + 5) + (2x - 3) can be rewritten as "
      "(x + 2x) + (5 - 3). Adding these like terms results in 3x + 2.\n"
      "\n"
      "Choice A is incorrect and may result from adding (x - 5) + (2x + 3).\n"
      "\n"
      "Choice C is incorrect and may result from adding (x - 5) + (2x - 3).\n"
      "\n"
      "Choice D is incorrect and may result from adding (x + 5) + (2x + 3)."
    ),
  },
  "52931bfa": {
    "prompt": "Which expression is equivalent to (8x(x - 7) - 3(x - 7))/(2x - 14), where x > 7?",
    "choices": [
      {"text": "(x - 7)/5"},
      {"text": "(8x - 3)/2"},
      {"text": "(8x^2 - 3x - 14)/(2x - 14)"},
      {"text": "(8x^2 - 3x - 77)/(2x - 14)"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. The given expression has a common factor of 2 in the denominator, so the expression can be rewritten as "
      "(8x(x - 7) - 3(x - 7))/(2(x - 7)). "
      "The three terms in this expression have a common factor of (x - 7). Since it's given that x > 7, x can't be equal to 7, which means (x - 7) "
      "can't be equal to 0. Therefore, each term in the expression, (8x(x - 7) - 3(x - 7))/(2(x - 7)), can be divided by (x - 7), which gives (8x - 3)/2.\n"
      "\n"
      "Choice A is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice C is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
  },
  "8490cc45": {
    "prompt": "The function f is defined by f(x) = (-8)(2)^x + 22. What is the y-intercept of the graph of y = f(x) in the xy-plane?",
    "choices": [
      {"text": "(0, 14)"},
      {"text": "(0, 2)"},
      {"text": "(0, 22)"},
      {"text": "(0, -8)"},
    ],
    "answer": 0,
    "equations": [],
    "explanation": (
      "Choice A is correct. The y-intercept of the graph of y = f(x) in the xy-plane occurs at the point on the graph where x = 0. In other words, when "
      "x = 0, the corresponding value of f(x) is the y-coordinate of the y-intercept. Substituting 0 for x in the given equation yields f(0) = (-8)(2)^0 + 22, "
      "which is equivalent to f(0) = (-8)(1) + 22, or f(0) = 14. Thus, when x = 0, the corresponding value of f(x) is 14. Therefore, the y-"
      "intercept of the graph of y = f(x) in the xy-plane is (0, 14).\n"
      "\n"
      "Choice B is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice C is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice D is incorrect. This could be the y-intercept for f(x) = (-8)(2)^x, not f(x) = (-8)(2)^x + 22."
    ),
  },
  "39714777": {
    "prompt": "p(x) + 57 = x^2\nThe given equation relates the value of x and its corresponding value of p(x) for the function p. What is the minimum value of the function p?",
    "choices": [
      {"text": "-3,249"},
      {"text": "-57"},
      {"text": "57"},
      {"text": "3,249"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. For a quadratic function defined by an equation of the form p(x) = a(x - h)^2 + k, where a, h, and k are constants and a > 0, "
      "the minimum value of the function is k. Subtracting 57 from both sides of the given equation yields p(x) = x^2 - 57. This function is in the "
      "form p(x) = a(x - h)^2 + k, where a = 1, h = 0, and k = -57. Therefore, the minimum value of the function p is -57.\n"
      "\n"
      "Choice A is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice C is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
  },
  "075b29b0": {
    "prompt": "Which expression is equivalent to (9x^3 + 5x + 7) + (6x^3 + 5x^2 - 5)?",
    "choices": [
      {"text": "15x^6 + 5x^2 - 5x - 35"},
      {"text": "15x^3 + 10x^2 + 2"},
      {"text": "15x^6 + 5x^2 + 5x + 2"},
      {"text": "15x^3 + 5x^2 + 5x + 2"},
    ],
    "answer": 3,
    "equations": [],
    "explanation": (
      "Choice D is correct. The given expression can be rewritten as (9x^3 + 6x^3) + 5x^2 + 5x + (7 - 5). Combining like terms in this expression "
      "yields 15x^3 + 5x^2 + 5x + 2.\n"
      "\n"
      "Choice A is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice B is incorrect and may result from conceptual or calculation errors.\n"
      "\n"
      "Choice C is incorrect and may result from conceptual or calculation errors."
    ),
  },
  "2c6f214f": {
    "prompt": (
      "The first term of a sequence is 9. Each term after the first is 4 times the preceding term. If w represents the nth term of the sequence, which "
      "equation gives w in terms of n?"
    ),
    "choices": [
      {"text": "w = 4(9^n)"},
      {"text": "w = 4(9)^(n - 1)"},
      {"text": "w = 9(4^n)"},
      {"text": "w = 9(4)^(n - 1)"},
    ],
    "answer": 3,
    "equations": [],
    "explanation": (
      "Choice D is correct. Since w represents the nth term of the sequence and 9 is the first term of the sequence, the value of w is 9 when the value "
      "of n is 1. Since each term after the first is 4 times the preceding term, the value of w is 9(4) when the value of n is 2. Therefore, the value of w "
      "is 9(4)(4), or 9(4)^2, when the value of n is 3. More generally, the value of w is 9(4)^(n - 1) for a given value of n. Therefore, the equation "
      "w = 9(4)^(n - 1) gives w in terms of n.\n"
      "\n"
      "Choice A is incorrect. This equation describes a sequence for which the first term is 36, rather than 9, and each term after the first is 9, rather "
      "than 4, times the preceding term.\n"
      "\n"
      "Choice B is incorrect. This equation describes a sequence for which the first term is 4, rather than 9, and each term after the first is 9, rather than "
      "4, times the preceding term.\n"
      "\n"
      "Choice C is incorrect. This equation describes a sequence for which the first term is 36, rather than 9."
    ),
  },
  "4661e2a9": {
    "prompt": "x - y = 1\nx + y = x^2 - 3\nWhich ordered pair is a solution to the system of equations above?",
    "choices": [
      {"text": "(1 + √3, √3)"},
      {"text": "(√3, -√3)"},
      {"text": "(1 + √5, √5)"},
      {"text": "(√5, -1 + √5)"},
    ],
    "answer": 0,
    "equations": [],
    "explanation": (
      "Choice A is correct. The solution to the given system of equations can be found by solving the first equation for x, which gives x = y + 1, and "
      "substituting that value of x into the second equation which gives y + 1 + y = (y + 1)^2 - 3. Rewriting this equation by adding like terms and "
      "expanding (y + 1)^2 gives 2y + 1 = y^2 + 2y - 2. Subtracting 2y from both sides of this equation gives 1 = y^2 - 2. Adding 2 to both "
      "sides of this equation gives 3 = y^2. Therefore, it follows that y = ±√3. Substituting √3 for y in the first equation yields x - √3 = 1. "
      "Adding √3 to both sides of this equation yields x = 1 + √3. Therefore, the ordered pair (1 + √3, √3) is a solution to the given system of "
      "equations.\n"
      "\n"
      "Choice B is incorrect. Substituting √3 for x and -√3 for y in the first equation yields √3 - (-√3) = 1, or 2√3 = 1, which isn't a true "
      "statement.\n"
      "\n"
      "Choice C is incorrect. Substituting 1 + √5 for x and √5 for y in the second equation yields (1 + √5) + √5 = (1 + √5)^2 - 3, "
      "or 1 + 2√5 = 2√5 + 3, which isn't a true statement.\n"
      "\n"
      "Choice D is incorrect. Substituting √5 for x and (-1 + √5) for y in the second "
      "equation yields √5 + (-1 + √5) = (√5)^2 - 3, or 2√5 - 1 = 2, which isn't a true statement."
    ),
  },
  "ad2ec615": {
    "prompt": "x^4 - x^2 - 6\nWhich of the following is equivalent to the expression?",
    "choices": [
      {"text": "(x^2 + 1)(x^2 - 6)"},
      {"text": "(x^2 + 2)(x^2 - 3)"},
      {"text": "(x^2 + 3)(x^2 - 2)"},
      {"text": "(x^2 + 6)(x^2 - 1)"},
    ],
    "answer": 1,
    "equations": [],
    "explanation": (
      "Choice B is correct. The term x^4 can be factored as (x^2)(x^2). Factoring -6 as (2)(-3) yields values that add to -1, the coefficient of x^2 in the "
      "expression.\n"
      "\n"
      "Choices A, C, and D are incorrect and may result from finding factors of -6 that don't add to the coefficient of x^2 in the original expression."
    ),
  },
  "42c71eb5": {
    "prompt": "(2x + 5)^2 - (x - 2) + 2(x + 3)\nWhich of the following is equivalent to the expression above?",
    "choices": [
      {"text": "4x^2 + 21x + 33"},
      {"text": "4x^2 + 21x + 29"},
      {"text": "4x^2 + x + 29"},
      {"text": "4x^2 + x + 33"},
    ],
    "answer": 0,
    "equations": [],
    "explanation": (
      "Choice A is correct. The given expression can be rewritten as (2x + 5)^2 + (-1)(x - 2) + 2(x + 3). Applying the distributive property, the "
      "expression (-1)(x - 2) + 2(x + 3) can be rewritten as -1(x) + (-1)(-2) + 2(x) + 2(3), or -x + 2 + 2x + 6. Adding like terms "
      "yields x + 8. Substituting x + 8 for (-1)(x - 2) + 2(x + 3) in the given expression yields (2x + 5)^2 + x + 8. By the rules of exponents, "
      "the expression (2x + 5)^2 is equivalent to (2x + 5)(2x + 5). Applying the distributive property, this expression can be rewritten as "
      "2x(2x) + 2x(5) + 5(2x) + 5(5), or 4x^2 + 10x + 10x + 25. Adding like terms gives 4x^2 + 20x + 25. Substituting 4x^2 + 20x + 25 "
      "for (2x + 5)^2 in the rewritten expression yields 4x^2 + 20x + 25 + x + 8, and adding like terms yields 4x^2 + 21x + 33.\n"
      "\n"
      "Choices B, C, and D are incorrect. Choices C and D may result from rewriting the expression (2x + 5)^2 as 4x^2 + 25, instead of as "
      "4x^2 + 20x + 25. Choices B and C may result from rewriting the expression -(x - 2) as -x - 2, instead of -x + 2."
    ),
  },
}
