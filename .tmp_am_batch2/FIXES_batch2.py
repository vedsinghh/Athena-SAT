# Educator Bank 1 Advanced Math — batch 2 FIXES
# Apply onto mathQuestions.json entries by id.

FIXES = {
    "a05bd3a4": {
        "prompt": "Which of the following expressions is equivalent to x^2 - 5?",
        "equations": [],
        "choices": [
            {"text": "(x + √5)^2"},
            {"text": "(x - √5)^2"},
            {"text": "(x + √5)(x - √5)"},
            {"text": "(x + 5)(x - 1)"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. The expression can be written as a difference of squares x^2 - y^2, "
            "which can be factored as (x + y)(x - y). Here, y^2 = 5, so y = √5, and the expression therefore "
            "factors as (x + √5)(x - √5).\n\n"
            "Choices A and B are incorrect and may result from misunderstanding how to factor a difference of squares.\n\n"
            "Choice D is incorrect; (x + 5)(x - 1) can be rewritten as x^2 + 4x - 5, which is not equivalent to the original expression."
        ),
    },
    "f423771c": {
        "prompt": (
            "The table shows the exponential relationship between the number of years, x, since Hana started "
            "training in pole vault, and the estimated height h(x), in meters, of her best pole vault for that year. "
            "Which of the following functions best represents this relationship, where x ≤ 4?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/f423771c.jpg",
        "choices": [
            {"text": "h(x) = 1.12(0.23)^x"},
            {"text": "h(x) = 1.12(1.23)^x"},
            {"text": "h(x) = 1.23(0.12)^x"},
            {"text": "h(x) = 1.23(1.12)^x"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. The table shows an increasing exponential relationship between the number of years, x, "
            "since Hana started training in pole vault and the estimated height h(x), in meters, of her best pole vault for "
            "that year. The relationship can be written as h(x) = a(b)^x, where a and b are positive constants. It's given "
            "that when x = 0, h(x) = 1.23. Substituting 0 for x and 1.23 for h(x) in h(x) = a(b)^x yields 1.23 = a(b)^0, or "
            "a = 1.23. Substituting 1.23 for a in h(x) = a(b)^x yields h(x) = 1.23(b)^x. It's also given that when x = 2, "
            "h(x) = 1.54. Substituting 2 for x and 1.54 for h(x) in h(x) = 1.23(b)^x yields 1.54 = 1.23(b)^2. Dividing each "
            "side of this equation by 1.23 yields (b)^2 ≈ 1.252, or b is approximately equal to √1.252. Since b is positive, "
            "b is approximately equal to 1.12, or h(x) = 1.23(1.12)^x.\n\n"
            "Choice A is incorrect. When x = 0, the value of h(x) in this function is equal to 1.12 rather than 1.23, and it "
            "is decreasing rather than increasing.\n\n"
            "Choice B is incorrect. When x = 0, the value of h(x) in this function is equal to 1.12 rather than 1.23.\n\n"
            "Choice C is incorrect. This function is decreasing rather than increasing."
        ),
    },
    "ae05d37b": {
        "prompt": (
            "f(t) = 40,000(2)^(t/790)\n"
            "The function f gives the number of bacteria in a population t minutes after an initial observation. "
            "How much time, in minutes, does it take for the number of bacteria in the population to double?"
        ),
        "equations": [],
        "choices": [
            {"text": "2"},
            {"text": "790"},
            {"text": "1,580"},
            {"text": "40,000"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. It's given that t minutes after an initial observation, the number of bacteria in a "
            "population is 40,000(2)^(t/790). This expression consists of the initial number of bacteria, 40,000, multiplied "
            "by the expression (2)^(t/790). The time, in minutes, it takes for the number of bacteria to double is the "
            "increase in the value of t that causes the expression (2)^(t/790) to double. Since the base is 2, the expression "
            "(2)^(t/790) will double when the exponent increases by 1. Since the exponent of this expression is t/790, the "
            "exponent will increase by 1 when t increases by 790. Therefore, the time, in minutes, it takes for the number "
            "of bacteria in the population to double is 790.\n\n"
            "Choice A is incorrect. This is the base of the exponent, not the time it takes for the number of bacteria in "
            "the population to double.\n\n"
            "Choice C is incorrect. This is the number of minutes it takes for the population to double twice.\n\n"
            "Choice D is incorrect. This is the number of bacteria that are initially observed, not the time it takes for "
            "the number of bacteria in the population to double."
        ),
    },
    "ad03127d": {
        "prompt": (
            "6r = 7s + t\n"
            "The given equation relates the variables r, s, and t. Which equation correctly expresses s in terms of r and t?"
        ),
        "equations": [],
        "choices": [
            {"text": "s = 42r - t"},
            {"text": "s = 7(6r - t)"},
            {"text": "s = (6/7)r - t"},
            {"text": "s = (6r - t)/7"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. Subtracting t from both sides of the given equation yields 6r - t = 7s. Dividing both "
            "sides of this equation by 7 yields (6r - t)/7 = s. Therefore, the equation s = (6r - t)/7 correctly expresses "
            "s in terms of r and t.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "02add2d2": {
        "prompt": (
            "A company has a newsletter. In January 2018, there were 1,300 customers subscribed to the newsletter. For the "
            "next 24 months after January 2018, the total number of customers subscribed to the newsletter each month was "
            "7% greater than the total number subscribed the previous month. Which equation gives the total number of "
            "customers, c, subscribed to the company's newsletter m months after January 2018, where m ≤ 24?"
        ),
        "equations": [],
        "choices": [
            {"text": "c = 1,300(0.07)^m"},
            {"text": "c = 1,300(1.07)^m"},
            {"text": "c = 1,300(1.7)^m"},
            {"text": "c = 1,300(7)^m"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. It's given that in January 2018, there were 1,300 customers subscribed to a company's "
            "newsletter and for the next 24 months after January 2018, the total number of customers subscribed to the "
            "newsletter each month was 7% greater than the total number subscribed the previous month. It follows that this "
            "situation can be represented by the equation c = a(1.07)^m, where c is the total number of customers subscribed "
            "to the company's newsletter m months after January 2018, a is the number of customers subscribed to the "
            "newsletter in January 2018, and the total number of customers subscribed to the newsletter each month was 7% "
            "greater than the total number subscribed the previous month. Substituting 1,300 for a and m for the exponent "
            "in this equation yields c = 1,300(1.07)^m.\n\n"
            "Choice A is incorrect. This equation represents a situation where the total number of customers subscribed each "
            "month was less, not 7% greater, than the total number subscribed the previous month.\n\n"
            "Choice C is incorrect. This equation represents a situation where the total number of customers subscribed each "
            "month was 70%, not 7%, greater than the total number subscribed the previous month.\n\n"
            "Choice D is incorrect. This equation represents a situation where the total number of customers subscribed each "
            "month was 600%, not 7%, greater than the total number subscribed the previous month."
        ),
    },
    "369b7bb7": {
        "prompt": "The function g is defined by g(x) = √(8x + 1). What is the value of g(3)?",
        "equations": [],
        "choices": [
            {"text": "5/8"},
            {"text": "25/8"},
            {"text": "5"},
            {"text": "25"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. It's given that the function g is defined by g(x) = √(8x + 1). Substituting 3 for x in "
            "the given function yields g(3) = √(8(3) + 1), which is equivalent to √25, or 5. Therefore, the value of g(3) is 5.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect. This is the value of 8(3) + 1, not √(8(3) + 1)."
        ),
    },
    "3206b905": {
        "prompt": "Which of the following expressions is equivalent to 8x^10 - 8x^9 + 88x?",
        "equations": [],
        "choices": [
            {"text": "x(7x^10 - 7x^9 + 87x)"},
            {"text": "x(8^10 - 8^9 + 88)"},
            {"text": "8x(x^10 - x^9 + 11x)"},
            {"text": "8x(x^9 - x^8 + 11)"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. Since 8x is a common factor of each term in the given expression, the expression can be "
            "rewritten as 8x(x^9 - x^8 + 11).\n\n"
            "Choice A is incorrect. This expression is equivalent to 7x^11 - 7x^10 + 87x^2.\n\n"
            "Choice B is incorrect. This expression is equivalent to 8^10 x - 8^9 x + 88x.\n\n"
            "Choice C is incorrect. This expression is equivalent to 8x^11 - 8x^10 + 88x^2."
        ),
    },
    "7902bed0": {
        "prompt": (
            "A machine launches a softball from ground level. The softball reaches a maximum height of 51.84 meters above "
            "the ground at 1.8 seconds and hits the ground at 3.6 seconds. Which equation represents the height above ground "
            "h, in meters, of the softball t seconds after it is launched?"
        ),
        "equations": [],
        "choices": [
            {"text": "h = -t^2 + 3.6"},
            {"text": "h = -t^2 + 51.84"},
            {"text": "h = -16(t - 1.8)^2 - 3.6"},
            {"text": "h = -16(t - 1.8)^2 + 51.84"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. An equation representing the height above ground h, in meters, of a softball t seconds "
            "after it is launched by a machine from ground level can be written in the form h = -a(t - b)^2 + c, where a, b, "
            "and c are positive constants. In this equation, b represents the time, in seconds, at which the softball reaches "
            "its maximum height of c meters above the ground. It's given that this softball reaches a maximum height of 51.84 "
            "meters above the ground at 1.8 seconds; therefore, b = 1.8 and c = 51.84. Substituting 1.8 for b and 51.84 for c "
            "in the equation h = -a(t - b)^2 + c yields h = -a(t - 1.8)^2 + 51.84. It's also given that this softball hits the "
            "ground at 3.6 seconds; therefore, h = 0 when t = 3.6. Substituting 0 for h and 3.6 for t in the equation "
            "h = -a(t - 1.8)^2 + 51.84 yields 0 = -a(3.6 - 1.8)^2 + 51.84, which is equivalent to 0 = -a(1.8)^2 + 51.84, or "
            "0 = -3.24a + 51.84. Adding 3.24a to both sides of this equation yields 3.24a = 51.84. Dividing both sides of this "
            "equation by 3.24 yields a = 16. Substituting 16 for a in the equation h = -a(t - 1.8)^2 + 51.84 yields "
            "h = -16(t - 1.8)^2 + 51.84. Therefore, h = -16(t - 1.8)^2 + 51.84 represents the height above ground h, in meters, "
            "of this softball t seconds after it is launched.\n\n"
            "Choice A is incorrect. This equation represents a situation where the maximum height is 3.6 meters above the "
            "ground at 0 seconds, not 51.84 meters above the ground at 1.8 seconds.\n\n"
            "Choice B is incorrect. This equation represents a situation where the maximum height is 51.84 meters above the "
            "ground at 0 seconds, not 1.8 seconds.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "768b60d2": {
        "prompt": (
            "For the exponential function f, the value of f(0) is c, where c is a constant. Of the following equations that "
            "define the function f, which equation shows the value of c as the coefficient or the base?"
        ),
        "equations": [],
        "choices": [
            {"text": "f(x) = 22(1.5)^(x + 1)"},
            {"text": "f(x) = 33(1.5)^x"},
            {"text": "f(x) = 49.5(1.5)^(x - 1)"},
            {"text": "f(x) = 74.25(1.5)^(x - 2)"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. Each of the given choices is an equation of the form f(x) = a(b)^(x - k), where a, b, and k "
            "are constants. For an equation of this form, the coefficient, a, is equal to the value of the function when the "
            "exponent is equal to 0, or when x = k. It follows that in the equation f(x) = 33(1.5)^x, the coefficient, 33, is "
            "equal to the value of f(0). Substituting 0 for x in this equation yields f(0) = 33(1.5)^0, which is equivalent to "
            "f(0) = 33(1), or f(0) = 33. Thus, the value of c is 33 and the equation f(x) = 33(1.5)^x shows the value of c as "
            "the coefficient.\n\n"
            "Choice A is incorrect. This equation shows the value of f(-1), not f(0), as the coefficient.\n\n"
            "Choice C is incorrect. This equation shows the value of f(1), not f(0), as the coefficient.\n\n"
            "Choice D is incorrect. This equation shows the value of f(2), not f(0), as the coefficient."
        ),
    },
    "253985c2": {
        "prompt": "Which expression is equivalent to 6x + 5x + 4y?",
        "equations": [],
        "choices": [
            {"text": "15x"},
            {"text": "15y"},
            {"text": "11x + 4y"},
            {"text": "30x + 4y"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. In the given expression, 6x and 5x are like terms. Combining these like terms yields 11x. "
            "It follows that the expression 6x + 5x + 4y is equivalent to 11x + 4y.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "cc776a04": {
        "prompt": "Which of the following is an equivalent form of (1.5x - 2.4)^2 - (5.2x^2 - 6.4)?",
        "equations": [],
        "choices": [
            {"text": "-2.2x^2 + 1.6"},
            {"text": "-2.2x^2 + 11.2"},
            {"text": "-2.95x^2 - 7.2x + 12.16"},
            {"text": "-2.95x^2 - 7.2x + 0.64"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. The first expression (1.5x - 2.4)^2 can be rewritten as (1.5x - 2.4)(1.5x - 2.4). Applying "
            "the distributive property to this product yields (2.25x^2 - 3.6x - 3.6x + 5.76) - (5.2x^2 - 6.4). This difference "
            "can be rewritten as (2.25x^2 - 7.2x + 5.76) + (-1)(5.2x^2 - 6.4). Distributing the factor of -1 through the second "
            "expression yields 2.25x^2 - 7.2x + 5.76 - 5.2x^2 + 6.4. Regrouping like terms, the expression becomes "
            "(2.25x^2 - 5.2x^2) - 7.2x + (5.76 + 6.4). Combining like terms yields -2.95x^2 - 7.2x + 12.16.\n\n"
            "Choices A, B, and D are incorrect and likely result from errors made when applying the distributive property or "
            "combining the resulting like terms."
        ),
    },
    "4ac59df6": {
        "prompt": "Which expression is equivalent to (8yz)(y)(7z)?",
        "equations": [],
        "choices": [
            {"text": "56y^2z^2"},
            {"text": "56y^2z"},
            {"text": "56yz"},
            {"text": "16yz"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. The given expression can be rewritten as (8)(7)(y)(y)(z)(z), which is equivalent to "
            "(56)(y^2)(z^2), or 56y^2z^2.\n\n"
            "Choice B is incorrect. This expression is equivalent to (8yz)(y)(7).\n\n"
            "Choice C is incorrect. This expression is equivalent to (8z)(y)(7).\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "84e5e36c": {
        "prompt": (
            "y = 76\n"
            "y = x^2 - 5\n"
            "The graphs of the given equations in the xy-plane intersect at the point (x, y). What is a possible value of x?"
        ),
        "equations": [],
        "choices": [
            {"text": "-76/5"},
            {"text": "-9"},
            {"text": "5"},
            {"text": "76"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. Since the point (x, y) is an intersection point of the graphs of the given equations in the "
            "xy-plane, the pair (x, y) should satisfy both equations, and thus is a solution of the given system. According to "
            "the first equation, y = 76. Substituting 76 in place of y in the second equation yields x^2 - 5 = 76. Adding 5 to "
            "both sides of this equation yields x^2 = 81. Taking the square root of both sides of this equation yields two "
            "solutions: x = 9 and x = -9. Of these two solutions, only -9 is given as a choice.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect. This is the value of coordinate y, rather than x, of the intersection point (x, y)."
        ),
    },
    "ff2c1431": {
        "prompt": (
            "7m = 5(n + p)\n"
            "The given equation relates the positive numbers m, n, and p. Which equation correctly gives n in terms of m and p?"
        ),
        "equations": [],
        "choices": [
            {"text": "n = (5p)/(7m)"},
            {"text": "n = (7m)/5 - p"},
            {"text": "n = 5(7m) + p"},
            {"text": "n = 7m - 5 - p"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. It's given that the equation 7m = 5(n + p) relates the positive numbers m, n, and p. "
            "Dividing both sides of the given equation by 5 yields (7m)/5 = n + p. Subtracting p from both sides of this "
            "equation yields (7m)/5 - p = n, or n = (7m)/5 - p. It follows that the equation n = (7m)/5 - p correctly gives n "
            "in terms of m and p.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "6ce95fc8": {
        "prompt": (
            "2x^2 - 2 = 2x + 3\n"
            "Which of the following is a solution to the equation above?"
        ),
        "equations": [],
        "choices": [
            {"text": "2"},
            {"text": "1 - √11"},
            {"text": "1/2 + √11"},
            {"text": "(1 + √11)/2"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. A quadratic equation in the form ax^2 + bx + c = 0, where a, b, and c are constants, can be "
            "solved using the quadratic formula: x = (-b ± √(b^2 - 4ac))/(2a). Subtracting 2x + 3 from both sides of the given "
            "equation yields 2x^2 - 2x - 5 = 0. Applying the quadratic formula, where a = 2, b = -2, and c = -5, yields "
            "x = (2 ± √((-2)^2 - 4(2)(-5)))/(2(2)). This can be rewritten as x = (2 ± √(4 + 40))/4. Since √44 = √(4 · 11) = 2√11, "
            "the equation can be rewritten as x = (2 ± 2√11)/4. Dividing 2 from both the numerator and denominator yields "
            "x = (1 ± √11)/2. Of these two solutions, only (1 + √11)/2 is present among the choices. Thus, the correct choice is D.\n\n"
            "Choice A is incorrect and may result from a computational or conceptual error.\n\n"
            "Choice B is incorrect and may result from using -b ± √(b^2 - 4ac) instead of (-b ± √(b^2 - 4ac))/(2a) as the "
            "quadratic formula.\n\n"
            "Choice C is incorrect and may result from rewriting (1 + √11)/2 as 1/2 + √11 instead of 1/2 + (√11)/2."
        ),
    },
    "e53add44": {
        "prompt": (
            "S(n) = 38,000a^n\n"
            "The function S above models the annual salary, in dollars, of an employee n years after starting a job, where a "
            "is a constant. If the employee's salary increases by 4% each year, what is the value of a?"
        ),
        "equations": [],
        "choices": [
            {"text": "0.04"},
            {"text": "0.4"},
            {"text": "1.04"},
            {"text": "1.4"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. A model for a quantity S that increases by a certain percentage per time period n is an "
            "exponential function in the form S(n) = I(1 + r/100)^n, where I is the initial value at time n = 0 for r% annual "
            "increase. It's given that the annual increase in an employee's salary is 4%, so r = 4. The initial value can be "
            "found by substituting 0 for n in the given function, which yields S(0) = 38,000. Therefore, I = 38,000. "
            "Substituting these values for r and I into the form of the exponential function S(n) = I(1 + r/100)^n yields "
            "S(n) = 38,000(1 + 4/100)^n, or S(n) = 38,000(1.04)^n. Therefore, the value of a in the given function is 1.04.\n\n"
            "Choices A, B, and D are incorrect and may result from incorrectly representing the annual increase in the "
            "exponential function."
        ),
    },
    "4dd4efcf": {
        "prompt": (
            "f(x) = ax^2 + 4x + c\n"
            "In the given quadratic function, a and c are constants. The graph of y = f(x) in the xy-plane is a parabola that "
            "opens upward and has a vertex at the point (h, k), where h and k are constants. If k < 0 and f(-9) = f(3), which "
            "of the following must be true?\n"
            "I. c < 0\n"
            "II. a ≥ 1"
        ),
        "equations": [],
        "choices": [
            {"text": "I only"},
            {"text": "II only"},
            {"text": "I and II"},
            {"text": "Neither I nor II"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. It's given that the graph of y = f(x) in the xy-plane is a parabola with vertex (h, k). If "
            "f(-9) = f(3), then for the graph of y = f(x), the point with an x-coordinate of -9 and the point with an "
            "x-coordinate of 3 have the same y-coordinate. In the xy-plane, a parabola is a symmetric graph such that when two "
            "points have the same y-coordinate, these points are equidistant from the vertex, and the x-coordinate of the "
            "vertex is halfway between the x-coordinates of these two points. Therefore, for the graph of y = f(x), the points "
            "with x-coordinates -9 and 3 are equidistant from the vertex (h, k), and h is halfway between -9 and 3. The value "
            "that is halfway between -9 and 3 is (-9 + 3)/2, or -3. Therefore, h = -3. The equation defining f can also be "
            "written in vertex form, f(x) = a(x - h)^2 + k. Substituting -3 for h in this equation yields "
            "f(x) = a(x + 3)^2 + k, or f(x) = a(x^2 + 6x + 9) + k. This equation is equivalent to f(x) = ax^2 + 6ax + 9a + k. "
            "Since f(x) = ax^2 + 4x + c, it follows that 6a = 4 and c = 9a + k. Dividing both sides of the equation 6a = 4 by 6 "
            "yields a = 4/6, or a = 2/3. Since a = 2/3, it's not true that a ≥ 1. Therefore, statement II isn't true. "
            "Substituting 2/3 for a in the equation c = 9a + k yields c = 9(2/3) + k, or c = 6 + k. Subtracting 6 from both "
            "sides of this equation yields c - 6 = k. If k < 0, then c - 6 < 0, or c < 6. Since c could be any value less than "
            "6, it's not necessarily true that c < 0. Therefore, statement I isn't necessarily true. Thus, neither I nor II "
            "must be true.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors."
        ),
    },
    # --- may keep image choices (graphs/tables); fix prompt/figure; convert point/equation choices to text where possible ---
    "02060533": {
        "prompt": (
            "The table shows three values of x and their corresponding values of g(x), where g(x) = f(x)/(x + 3) and f is a "
            "linear function. What is the y-intercept of the graph of y = f(x) in the xy-plane?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/02060533.jpg",
        "choices": [
            {"text": "(0, 36)"},
            {"text": "(0, 12)"},
            {"text": "(0, 4)"},
            {"text": "(0, -9)"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. It's given that the table shows values of x and their corresponding values of g(x), where "
            "g(x) = f(x)/(x + 3). It's also given that f is a linear function. It follows that an equation that defines f can "
            "be written in the form f(x) = mx + b, where m represents the slope and b represents the y-coordinate of the "
            "y-intercept (0, b) of the graph of y = f(x) in the xy-plane. Since the table shows values of x and their "
            "corresponding values of g(x), substituting values of x and g(x) in the equation f(x) = g(x)(x + 3) can be used to "
            "define function f. Using the first pair of values from the table, x = -27 and g(x) = 3, yields "
            "f(-27) = 3(-27 + 3), or f(-27) = -72. Using the second pair of values from the table, x = -9 and g(x) = 0, yields "
            "f(-9) = 0(-9 + 3), or f(-9) = 0. Substituting (-27, -72) and (-9, 0) for (x1, y1) and (x2, y2), respectively, in "
            "the slope formula m = (y2 - y1)/(x2 - x1) yields m = (0 - (-72))/(-9 - (-27)), or m = 4. Substituting 4 for m in "
            "the equation f(x) = mx + b yields f(x) = 4x + b. Since f(-9) = 0, substituting -9 for x and 0 for f(x) in the "
            "equation f(x) = 4x + b yields 0 = 4(-9) + b, or 0 = -36 + b. Adding 36 to both sides of this equation yields "
            "b = 36. It follows that 36 is the y-coordinate of the y-intercept (0, b) of the graph of y = f(x). Therefore, the "
            "y-intercept of the graph of y = f(x) is (0, 36).\n\n"
            "Choice B is incorrect. 12 is the y-coordinate of the y-intercept of the graph of y = g(x).\n\n"
            "Choice C is incorrect. 4 is the slope of the graph of y = f(x).\n\n"
            "Choice D is incorrect. -9 is the x-coordinate of the x-intercept of the graph of y = f(x)."
        ),
    },
    "e9aed539": {
        "prompt": "The graph shown will be translated up 4 units. Which of the following will be the resulting graph?",
        "equations": [],
        "figure": "/qbank/math/figures/e9aed539.jpg",
        "choices": [
            {"image": "/qbank/math/choices/e9aed539_0.jpg"},
            {"image": "/qbank/math/choices/e9aed539_1.jpg"},
            {"image": "/qbank/math/choices/e9aed539_2.jpg"},
            {"image": "/qbank/math/choices/e9aed539_3.jpg"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. When a graph is translated up 4 units, each point on the resulting graph is 4 units above "
            "the point on the original graph. In other words, the y-value of each point on the graph increases by 4. The graph "
            "shown passes through the points (1, -1), (2, -2), and (3, -1). It follows that when the graph shown is translated "
            "up 4 units, the resulting graph will pass through the points (1, -1 + 4), (2, -2 + 4), and (3, -1 + 4). These "
            "points are (1, 3), (2, 2), and (3, 3), respectively. Of the given choices, only the graph in choice A passes "
            "through the points (1, 3), (2, 2), and (3, 3).\n\n"
            "Choice B is incorrect. This is the result of translating the graph down, rather than up, 4 units.\n\n"
            "Choice C is incorrect. This is the result of translating the graph left, rather than up, 4 units.\n\n"
            "Choice D is incorrect. This is the result of translating the graph right, rather than up, 4 units."
        ),
    },
    "6abec9a8": {
        "prompt": "What is the y-intercept of the graph shown?",
        "equations": [],
        "figure": "/qbank/math/figures/6abec9a8.jpg",
        "choices": [
            {"text": "(-1, -9)"},
            {"text": "(0, -5)"},
            {"text": "(0, -4)"},
            {"text": "(0, 0)"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. The y-intercept of a graph in the xy-plane is the point on the graph where x = 0. At x = 0, "
            "the corresponding value of y is -5. Therefore, the y-intercept of the graph shown is (0, -5).\n\n"
            "Choice A is incorrect and may result from conceptual errors.\n\n"
            "Choice C is incorrect. This is the y-intercept of a graph in the xy-plane that intersects the y-axis at "
            "(0, -4), not (0, -5).\n\n"
            "Choice D is incorrect. This is the y-intercept of a graph in the xy-plane that intersects the y-axis at "
            "(0, 0), not (0, -5)."
        ),
    },
    "ff8c5844": {
        "prompt": (
            "For the exponential function g, the table shows four values of x and their corresponding values of g(x). "
            "Which equation defines g?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/ff8c5844.jpg",
        "choices": [
            {"text": "g(x) = -25^x"},
            {"text": "g(x) = -(1/25)^x"},
            {"text": "g(x) = 25^x"},
            {"text": "g(x) = (1/25)^x"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. It's given that function g is exponential. Therefore, an equation defining g can be written "
            "in the form g(x) = a(b)^x, where a and b are constants. The table shows that when x = 0, g(x) = 1. Substituting 0 "
            "for x and 1 for g(x) in the equation g(x) = a(b)^x yields 1 = a(b)^0, which is equivalent to a = 1. Substituting 1 "
            "for a in the equation g(x) = a(b)^x yields g(x) = (b)^x. The table also shows that when x = -1, g(x) = 25. "
            "Substituting -1 for x and 25 for g(x) in the equation g(x) = (b)^x yields 25 = (b)^(-1), which is equivalent to "
            "b = 1/25. Substituting 1/25 for b in the equation g(x) = (b)^x yields g(x) = (1/25)^x.\n\n"
            "Choice A is incorrect. For this function, g(0) is equal to -1, not 1.\n\n"
            "Choice B is incorrect. For this function, g(0) is equal to -1, not 1.\n\n"
            "Choice C is incorrect. For this function, g(-1) is equal to 1/25, not 25."
        ),
    },
    "1ee962ec": {
        "prompt": (
            "Scientists recorded data about the ocean water levels at a certain location over a period of 6 hours. The graph "
            "shown models the data, where y = 0 represents sea level. Which table gives values of x and their corresponding "
            "values of y based on the model?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/1ee962ec.jpg",
        "choices": [
            {"image": "/qbank/math/choices/1ee962ec_0.jpg"},
            {"image": "/qbank/math/choices/1ee962ec_1.jpg"},
            {"image": "/qbank/math/choices/1ee962ec_2.jpg"},
            {"image": "/qbank/math/choices/1ee962ec_3.jpg"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. Each point on the graph represents an elapsed time x, in hours, and the corresponding ocean "
            "water level y, in feet, at a certain location based on the model. The graph shown passes through the points "
            "(0, 0), (3, -12), and (6, 0). Thus, the table in choice C gives the values of x and their corresponding values of "
            "y based on the model.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "252a3b3a": {
        "prompt": "Which of the following could be the equation of the graph shown in the xy-plane?",
        "equations": [],
        "figure": "/qbank/math/figures/252a3b3a.jpg",
        "choices": [
            {"text": "y = -(1/10)x(x - 4)(x + 5)"},
            {"text": "y = -(1/10)x(x - 4)(x + 5)^2"},
            {"text": "y = -(1/10)x(x - 5)(x + 4)"},
            {"text": "y = -(1/10)x(x - 5)^2(x + 4)"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. Each of the given choices is an equation of the form y = -a x^b (x - c)^d (x + e)^f, where "
            "a, b, c, d, e, and f are positive constants. In the xy-plane, the graph of an equation of this form has "
            "x-intercepts at x = 0, x = c, and x = -e. The graph shown has x-intercepts at x = 0, x = 4, and x = -5. Therefore, "
            "c = 4 and e = 5. Of the given choices, only choices A and B have c = 4 and e = 5. For an equation in the form "
            "y = -a x^b (x - c)^d (x + e)^f, if all values of x that are less than -e or greater than c correspond to negative "
            "y-values, then the sum of all the exponents of the factors on the right-hand side of the equation is even. In the "
            "graph shown, all values of x less than -5 or greater than 4 correspond to negative y-values. Therefore, the sum "
            "of all the exponents of the factors on the right-hand side of the equation must be even. For choice A, the sum of "
            "these exponents is 1 + 1 + 1, or 3, which is odd. For choice B, the sum of these exponents is 1 + 1 + 2, or 4, "
            "which is even. Therefore, y = -(1/10)x(x - 4)(x + 5)^2 could be the equation of the graph shown.\n\n"
            "Choice A is incorrect. For the graph of this equation, all values of x less than -5 correspond to positive, not "
            "negative, y-values.\n\n"
            "Choice C is incorrect. The graph of this equation has x-intercepts at x = 0, x = 5, and x = -4, rather than "
            "x-intercepts at x = 0, x = 4, and x = -5.\n\n"
            "Choice D is incorrect. The graph of this equation has x-intercepts at x = 0, x = 5, and x = -4, rather than "
            "x-intercepts at x = 0, x = 4, and x = -5."
        ),
    },
}
