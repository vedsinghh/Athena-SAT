# Educator Bank 1 Advanced Math — batch 3 FIXES
# Apply onto mathQuestions.json entries by id.

FIXES = {
    "72ebc024": {
        "prompt": "Which expression is equivalent to 16x^3y^2 + 14xy?",
        "equations": [],
        "choices": [
            {"text": "2xy(8xy + 7)"},
            {"text": "2xy(8x^2y + 7)"},
            {"text": "14xy(2x^2y + 1)"},
            {"text": "14xy(8x^2y + 1)"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. Since 2xy is a common factor of each term in the given expression, the expression can be "
            "rewritten as 2xy(8x^2y + 7).\n\n"
            "Choice A is incorrect. This expression is equivalent to 16x^2y^2 + 14xy.\n\n"
            "Choice C is incorrect. This expression is equivalent to 28x^3y^2 + 14xy.\n\n"
            "Choice D is incorrect. This expression is equivalent to 112x^3y^2 + 14xy."
        ),
    },
    "332cd67b": {
        "prompt": (
            "3x^2 - 15x + 18 = 0\n"
            "How many distinct real solutions are there to the given equation?"
        ),
        "equations": [],
        "choices": [
            {"text": "Exactly one"},
            {"text": "Exactly two"},
            {"text": "Infinitely many"},
            {"text": "Zero"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. The number of solutions to a quadratic equation of the form ax^2 + bx + c = 0, where a, b, "
            "and c are constants, can be determined by the value of the discriminant, b^2 - 4ac. If the value of the "
            "discriminant is positive, then the equation has exactly two distinct real solutions. For the given equation, "
            "a = 3, b = -15, and c = 18, so the discriminant is (-15)^2 - 4(3)(18) = 225 - 216 = 9. Since the value of the "
            "discriminant is positive, the given equation has exactly two distinct real solutions.\n\n"
            "Choice A is incorrect. A quadratic equation has exactly one distinct real solution when the discriminant is "
            "equal to 0, not when the discriminant is positive.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect. A quadratic equation has zero distinct real solutions when the discriminant is "
            "negative, not when the discriminant is positive."
        ),
    },
    "128c75e2": {
        "prompt": (
            "The function g is defined by g(x) = |x|/a - 14, where a < 0. What is the product of g(15a) and g(7a)?"
        ),
        "equations": [],
        "choices": [],
        "answer": 609,
        "acceptedAnswers": ["609"],
        "explanation": (
            "The correct answer is 609. It's given that the function g is defined by g(x) = |x|/a - 14, where a < 0. "
            "Substituting 15a for x in function g yields g(15a) = |15a|/a - 14. This function can be rewritten as "
            "g(15a) = 15|a|/a - 14, or g(15a) = 15(|a|/a) - 14. Since a < 0, it follows that |a|/a = -1. Substituting -1 "
            "for |a|/a in g(15a) = 15(|a|/a) - 14 yields g(15a) = 15(-1) - 14, or g(15a) = -29. Similarly, substituting 7a "
            "for x in function g yields g(7a) = |7a|/a - 14. This function can be rewritten as g(7a) = 7|a|/a - 14, or "
            "g(7a) = 7(|a|/a) - 14. Since a < 0, it again follows that |a|/a = -1. Substituting -1 for |a|/a in "
            "g(7a) = 7(|a|/a) - 14 yields g(7a) = 7(-1) - 14, or g(7a) = -21. Therefore, g(15a) = -29 and g(7a) = -21. "
            "Thus, the product of g(15a) and g(7a) is (-29)(-21), or 609."
        ),
    },
    "358f18bc": {
        "prompt": (
            "f(x) = x^2 - 48x + 2,304\n"
            "What is the minimum value of the given function?"
        ),
        "equations": [],
        "choices": [],
        "answer": 1728,
        "acceptedAnswers": ["1728", "1,728"],
        "explanation": (
            "The correct answer is 1,728. The given function can be rewritten in the form f(x) = a(x - h)^2 + k, where a "
            "is a positive constant and the minimum value, k, of the function occurs when the value of x is h. By completing "
            "the square, f(x) = x^2 - 48x + 2,304 can be written as "
            "f(x) = x^2 - 48x + (48/2)^2 + 2,304 - (48/2)^2, or f(x) = (x - 24)^2 + 1,728. This equation is in the form "
            "f(x) = a(x - h)^2 + k, where a = 1, h = 24, and k = 1,728. Therefore, the minimum value of the given function "
            "is 1,728."
        ),
    },
    "ebed7dc6": {
        "prompt": (
            "An auditorium has seats for 1,800 people. Tickets to attend a show at the auditorium currently cost $4.00. "
            "For each $1.00 increase to the ticket price, 100 fewer tickets will be sold. This situation can be modeled by "
            "the equation y = -100x^2 + 1,400x + 7,200, where x represents the increase in ticket price, in dollars, and y "
            "represents the revenue, in dollars, from ticket sales. If this equation is graphed in the xy-plane, at what "
            "value of x is the maximum of the graph?"
        ),
        "equations": [],
        "choices": [
            {"text": "4"},
            {"text": "7"},
            {"text": "14"},
            {"text": "18"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. It's given that the situation can be modeled by the equation "
            "y = -100x^2 + 1,400x + 7,200, where x represents the increase in ticket price, in dollars, and y represents "
            "the revenue, in dollars, from ticket sales. Since the coefficient of the x^2 term is negative, the graph of "
            "this equation in the xy-plane opens downward and reaches its maximum value at its vertex. If a quadratic "
            "equation in the form y = ax^2 + bx + c, where a, b, and c are constants, is graphed in the xy-plane, the "
            "x-coordinate of the vertex is equal to -b/(2a). For the equation y = -100x^2 + 1,400x + 7,200, a = -100, "
            "b = 1,400, and c = 7,200. It follows that the x-coordinate of the vertex is -1,400/(2(-100)), or 7. Therefore, "
            "if the given equation is graphed in the xy-plane, the maximum of the graph occurs at an x-value of 7.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "fc3d783a": {
        "prompt": (
            "In the xy-plane, a line with equation 2y = 4.5 intersects a parabola at exactly one point. If the parabola "
            "has equation y = -4x^2 + bx, where b is a positive constant, what is the value of b?"
        ),
        "equations": [],
        "choices": [],
        "answer": 6,
        "acceptedAnswers": ["6"],
        "explanation": (
            "The correct answer is 6. It's given that a line with equation 2y = 4.5 intersects a parabola with equation "
            "y = -4x^2 + bx, where b is a positive constant, at exactly one point in the xy-plane. It follows that the "
            "system of equations consisting of 2y = 4.5 and y = -4x^2 + bx has exactly one solution. Dividing both sides "
            "of the equation of the line by 2 yields y = 2.25. Substituting 2.25 for y in the equation of the parabola "
            "yields 2.25 = -4x^2 + bx. Adding 4x^2 and subtracting bx from both sides of this equation yields "
            "4x^2 - bx + 2.25 = 0. A quadratic equation in the form of ax^2 + bx + c = 0, where a, b, and c are constants, "
            "has exactly one solution when the discriminant, b^2 - 4ac, is equal to zero. Substituting 4 for a and 2.25 "
            "for c in the expression b^2 - 4ac and setting this expression equal to 0 yields b^2 - 4(4)(2.25) = 0, or "
            "b^2 - 36 = 0. Adding 36 to each side of this equation yields b^2 = 36. Taking the square root of each side of "
            "this equation yields b = ±6. It's given that b is positive, so the value of b is 6."
        ),
    },
    "a9084ca4": {
        "prompt": (
            "f(x) = 9,000(0.66)^x\n"
            "The given function f models the number of advertisements a company sent to its clients each year, where x "
            "represents the number of years since 1997, and 0 ≤ x ≤ 5. If y = f(x) is graphed in the xy-plane, which of "
            "the following is the best interpretation of the y-intercept of the graph in this context?"
        ),
        "equations": [],
        "choices": [
            {"text": "The minimum estimated number of advertisements the company sent to its clients during the 5 years was 1,708."},
            {"text": "The minimum estimated number of advertisements the company sent to its clients during the 5 years was 9,000."},
            {"text": "The estimated number of advertisements the company sent to its clients in 1997 was 1,708."},
            {"text": "The estimated number of advertisements the company sent to its clients in 1997 was 9,000."},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. The y-intercept of a graph in the xy-plane is the point where x = 0. For the given "
            "function f, the y-intercept of the graph of y = f(x) in the xy-plane can be found by substituting 0 for x in "
            "the equation y = 9,000(0.66)^x, which gives y = 9,000(0.66)^0. This is equivalent to y = 9,000(1), or "
            "y = 9,000. Therefore, the y-intercept of the graph of y = f(x) is (0, 9,000). It's given that the function f "
            "models the number of advertisements a company sent to its clients each year. Therefore, f(x) represents the "
            "estimated number of advertisements the company sent to its clients each year. It's also given that x "
            "represents the number of years since 1997. Therefore, x = 0 represents 0 years since 1997, or 1997. Thus, "
            "the best interpretation of the y-intercept of the graph of y = f(x) is that the estimated number of "
            "advertisements the company sent to its clients in 1997 was 9,000.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "781c2f6e": {
        "prompt": (
            "The function f is defined by f(x) = a(2.2^x + 2.2^b), where a and b are integer constants and 0 < a < b. "
            "The functions g and h are equivalent to function f, where k and m are constants. Which of the following "
            "equations displays the y-coordinate of the y-intercept of the graph of y = f(x) in the xy-plane as a "
            "constant or coefficient?\n"
            "I. g(x) = a(2.2^x + k)\n"
            "II. h(x) = a(2.2)^x + m"
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
            "Choice D is correct. A y-intercept of a graph in the xy-plane is a point where the graph intersects the "
            "y-axis, or a point where x = 0. Substituting 0 for x in the equation defining function f yields "
            "f(0) = a(2.2^0 + 2.2^b), or f(0) = a(1 + 2.2^b). So, the y-coordinate of the y-intercept of the graph is "
            "a(1 + 2.2^b), or equivalently, a + a(2.2)^b. It's given that function g is equivalent to function f, where "
            "0 < a < b. It follows that k = 2.2^b. Since a(2.2)^b can't be equal to 0, the coefficient a can't be equal to "
            "a + a(2.2)^b. Since 0 < a, the constant k, which is equal to 2.2^b, can't be equal to a + a(2.2)^b. Therefore, "
            "function g doesn't display the y-coordinate of the y-intercept of the graph of y = f(x) in the xy-plane as a "
            "constant or coefficient. It's also given that function h is equivalent to function f, where 0 < a < b. The "
            "equation defining f can be rewritten as f(x) = a(2.2)^x + a(2.2)^b. It follows that m = a(2.2)^b. Since "
            "a(2.2)^b can't be equal to 0, the coefficient a can't be equal to a + a(2.2)^b. Since 0 < a, the constant m, "
            "which is equal to a(2.2)^b, can't be equal to a + a(2.2)^b. Therefore, function h doesn't display the "
            "y-coordinate of the y-intercept of the graph of y = f(x) in the xy-plane as a constant or coefficient. Thus, "
            "neither function g nor function h displays the y-coordinate of the y-intercept of the graph of y = f(x) in "
            "the xy-plane as a constant or coefficient.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "cb29c54c": {
        "prompt": (
            "y = -16(x - 5.6)^2 + 502\n"
            "A physics class is planning an experiment about a toy rocket. The equation above gives the estimated height "
            "y, in feet, of the toy rocket x seconds after it is launched into the air. Which of the following is the "
            "best interpretation of the vertex of the graph of the equation in the xy-plane?"
        ),
        "equations": [],
        "choices": [
            {"text": "This toy rocket reaches an estimated maximum height of 502 feet 16 seconds after it is launched into the air."},
            {"text": "This toy rocket reaches an estimated maximum height of 502 feet 5.6 seconds after it is launched into the air."},
            {"text": "This toy rocket reaches an estimated maximum height of 16 feet 502 seconds after it is launched into the air."},
            {"text": "This toy rocket reaches an estimated maximum height of 5.6 feet 502 seconds after it is launched into the air."},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. The vertex of the graph of a quadratic equation is where it reaches its minimum or "
            "maximum value. When a quadratic equation is written in the form y = a(x - h)^2 + k, the vertex of the graph "
            "of the equation is (h, k). For the given equation, h = 5.6 and k = 502. Since the coefficient of the squared "
            "term is negative, the graph opens downward and the vertex represents the maximum value of the function. "
            "Therefore, the toy rocket reaches an estimated maximum height of 502 feet 5.6 seconds after it is launched "
            "into the air.\n\n"
            "Choice A is incorrect. The value 16 is the absolute value of the leading coefficient, not the time at which "
            "the maximum height occurs.\n\n"
            "Choice C is incorrect. This choice swaps the height and time values and incorrectly uses 16 as the height.\n\n"
            "Choice D is incorrect. This choice swaps the height and time values from the vertex."
        ),
    },
    "371cbf6b": {
        "prompt": (
            "(ax + 3)(5x^2 - bx + 4) = 20x^3 - 9x^2 - 2x + 12\n"
            "The equation above is true for all x, where a and b are constants. What is the value of ab?"
        ),
        "equations": [],
        "choices": [
            {"text": "18"},
            {"text": "20"},
            {"text": "24"},
            {"text": "40"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. If the equation is true for all x, then the expressions on both sides of the equation "
            "will be equivalent. Multiplying the polynomials on the left-hand side of the equation gives "
            "5ax^3 - abx^2 + 4ax + 15x^2 - 3bx + 12. On the right-hand side of the equation, the only x^2-term is -9x^2. "
            "Since the expressions on both sides of the equation are equivalent, it follows that -abx^2 + 15x^2 = -9x^2, "
            "which can be rewritten as (-ab + 15)x^2 = -9x^2. Therefore, -ab + 15 = -9, which gives ab = 24.\n\n"
            "Choice A is incorrect. If ab = 18, then the coefficient of x^2 on the left-hand side of the equation would be "
            "-18 + 15 = -3, which doesn't equal the coefficient of x^2, -9, on the right-hand side.\n\n"
            "Choice B is incorrect. If ab = 20, then the coefficient of x^2 on the left-hand side of the equation would be "
            "-20 + 15 = -5, which doesn't equal the coefficient of x^2, -9, on the right-hand side.\n\n"
            "Choice D is incorrect. If ab = 40, then the coefficient of x^2 on the left-hand side of the equation would be "
            "-40 + 15 = -25, which doesn't equal the coefficient of x^2, -9, on the right-hand side."
        ),
    },
    "b4acba95": {
        "prompt": (
            "x^2 - 12x + 27 = 0\n"
            "How many distinct real solutions does the given equation have?"
        ),
        "equations": [],
        "choices": [
            {"text": "Exactly two"},
            {"text": "Exactly one"},
            {"text": "Zero"},
            {"text": "Infinitely many"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. The number of solutions of a quadratic equation of the form ax^2 + bx + c = 0, where "
            "a, b, and c are constants, can be determined by the value of the discriminant, b^2 - 4ac. If the value of "
            "the discriminant is positive, then the equation has exactly two distinct real solutions. For the given "
            "equation, a = 1, b = -12, and c = 27, so the discriminant is (-12)^2 - 4(1)(27) = 144 - 108 = 36. Since the "
            "value of the discriminant is positive, the given equation has exactly two distinct real solutions.\n\n"
            "Choice B is incorrect. A quadratic equation has exactly one distinct real solution when the discriminant is "
            "equal to 0, not when the discriminant is positive.\n\n"
            "Choice C is incorrect. A quadratic equation has zero distinct real solutions when the discriminant is "
            "negative, not when the discriminant is positive.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "c3b116d7": {
        "prompt": (
            "Which of the following expressions is(are) a factor of 3x^2 + 20x - 63?\n"
            "I. x - 9\n"
            "II. 3x - 7"
        ),
        "equations": [],
        "choices": [
            {"text": "I only"},
            {"text": "II only"},
            {"text": "I and II"},
            {"text": "Neither I nor II"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. The given expression can be factored by first finding two values whose sum is 20 and "
            "whose product is 3(-63), or -189. Those two values are 27 and -7. It follows that the given expression can be "
            "rewritten as 3x^2 + 27x - 7x - 63, which is equivalent to 3x(x + 9) - 7(x + 9), or (3x - 7)(x + 9). "
            "Therefore, 3x - 7 is a factor of the given expression, and x - 9 is not.\n\n"
            "Choice A is incorrect. The expression x - 9 is not a factor of 3x^2 + 20x - 63.\n\n"
            "Choice C is incorrect. The expression x - 9 is not a factor of 3x^2 + 20x - 63.\n\n"
            "Choice D is incorrect. The expression 3x - 7 is a factor of 3x^2 + 20x - 63."
        ),
    },
    "b8f13a3a": {
        "prompt": (
            "Function f is defined by f(x) = -a^x + b, where a and b are constants. In the xy-plane, the graph of "
            "y = f(x) - 12 has a y-intercept at (0, -75/7). The product of a and b is 320/7. What is the value of a?"
        ),
        "equations": [],
        "choices": [],
        "answer": 20,
        "acceptedAnswers": ["20"],
        "explanation": (
            "The correct answer is 20. It's given that f(x) = -a^x + b. Substituting -a^x + b for f(x) in the equation "
            "y = f(x) - 12 yields y = -a^x + b - 12. It's given that the y-intercept of the graph of y = f(x) - 12 is "
            "(0, -75/7). Substituting 0 for x and -75/7 for y in the equation y = -a^x + b - 12 yields "
            "-75/7 = -a^0 + b - 12, which is equivalent to -75/7 = -1 + b - 12, or -75/7 = b - 13. Adding 13 to both sides "
            "of this equation yields 16/7 = b. It's given that the product of a and b is 320/7, or ab = 320/7. Substituting "
            "16/7 for b in this equation yields (a)(16/7) = 320/7. Dividing both sides of this equation by 16/7 yields a = 20."
        ),
    },
    "8e1da169": {
        "prompt": (
            "f(x) = (x - 44)(x - 46)\n"
            "The function f is defined by the given equation. For what value of x does f(x) reach its minimum?"
        ),
        "equations": [],
        "choices": [
            {"text": "46"},
            {"text": "45"},
            {"text": "44"},
            {"text": "-1"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. It's given that f(x) = (x - 44)(x - 46), which can be rewritten as "
            "f(x) = x^2 - 90x + 2,024. Since the coefficient of the x^2-term is positive, the graph of y = f(x) in the "
            "xy-plane opens upward and reaches its minimum value at its vertex. For an equation in the form "
            "f(x) = ax^2 + bx + c, where a, b, and c are constants, the x-coordinate of the vertex is -b/(2a). For the "
            "equation f(x) = x^2 - 90x + 2,024, a = 1, b = -90, and c = 2,024. It follows that the x-coordinate of the "
            "vertex is -(-90)/(2(1)), or 45. Therefore, f(x) reaches its minimum when the value of x is 45.\n\n"
            "Choice A is incorrect. This is one of the x-coordinates of the x-intercepts of the graph of y = f(x) in the "
            "xy-plane.\n\n"
            "Choice C is incorrect. This is one of the x-coordinates of the x-intercepts of the graph of y = f(x) in the "
            "xy-plane.\n\n"
            "Choice D is incorrect. This is the y-coordinate of the vertex of the graph of y = f(x) in the xy-plane."
        ),
    },
    "c6a26e14": {
        "prompt": (
            "|x + 45| = 48\n"
            "What is the positive solution to the given equation?"
        ),
        "equations": [],
        "choices": [
            {"text": "3"},
            {"text": "48"},
            {"text": "93"},
            {"text": "96"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. By the definition of absolute value, the equation |x + 45| = 48 is equivalent to "
            "x + 45 = 48 or x + 45 = -48. Solving these equations yields x = 3 or x = -93. Therefore, the positive "
            "solution to the given equation is 3.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect. This is the absolute value of the negative solution, not the positive solution.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "07bcecac": {
        "prompt": (
            "P(t) = 24.8(1.036)^t\n"
            "The function P gives the predicted population, in millions, of a certain country for the period from 1984 "
            "to 2018, where t is the number of years after 1984. According to the model, what is the best interpretation "
            "of the statement \"P(8) is approximately equal to 32.91\"?"
        ),
        "equations": [],
        "choices": [
            {"text": "In 1984, the predicted population of this country was approximately 8 million."},
            {"text": "In 1984, the predicted population of this country was approximately 32.91 million."},
            {"text": "8 years after 1984, the predicted population of this country was approximately 32.91 million."},
            {"text": "32.91 years after 1984, the predicted population of this country was approximately 8 million."},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. It's given that the function P gives the predicted population, in millions, of a "
            "certain country for the period from 1984 to 2018, where t is the number of years after 1984. Therefore, "
            "P(8) represents the predicted population, in millions, of this country 8 years after 1984. It's also given "
            "that P(8) is approximately equal to 32.91. Thus, 8 years after 1984, the predicted population of this "
            "country was approximately 32.91 million.\n\n"
            "Choice A is incorrect. This interprets t = 8 as the predicted population in 1984 rather than 8 years after "
            "1984.\n\n"
            "Choice B is incorrect. This interprets P(8) as the predicted population in 1984 rather than 8 years after "
            "1984.\n\n"
            "Choice D is incorrect. This swaps the meanings of the input and output of the function."
        ),
    },
    "f65288e8": {
        "prompt": (
            "1/(x^2 + 10x + 25) = 4\n"
            "If x is a solution to the given equation, which of the following is a possible value of x + 5?"
        ),
        "equations": [],
        "choices": [
            {"text": "1/2"},
            {"text": "5/2"},
            {"text": "9/2"},
            {"text": "11/2"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. The given equation can be rewritten as 1/(x + 5)^2 = 4. Multiplying both sides of this "
            "equation by (x + 5)^2 yields 1 = 4(x + 5)^2. Dividing both sides of this equation by 4 yields "
            "1/4 = (x + 5)^2. Taking the square root of both sides of this equation yields 1/2 = x + 5 or "
            "-1/2 = x + 5. Therefore, a possible value of x + 5 is 1/2.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "788bfd56": {
        "prompt": "The function f is defined by f(x) = 4 + sqrt(x). What is the value of f(144)?",
        "equations": [],
        "choices": [
            {"text": "0"},
            {"text": "16"},
            {"text": "40"},
            {"text": "76"},
        ],
        "answer": 1,
        "explanation": (
            "Choice B is correct. Substituting 144 for x in the given function yields f(144) = 4 + sqrt(144). Since "
            "sqrt(144) = 12, it follows that f(144) = 4 + 12, or 16.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect. This is the value of f(1,296), not f(144).\n\n"
            "Choice D is incorrect. This is the value of f(5,184), not f(144)."
        ),
    },
    "40491607": {
        "prompt": (
            "f(x) = (x - 1)(x + 3)(x - 2)\n"
            "In the xy-plane, when the graph of the function f, where y = f(x), is shifted up 6 units, the resulting "
            "graph is defined by the function g. If the graph of y = g(x) crosses through the point (4, b), where b is a "
            "constant, what is the value of b?"
        ),
        "equations": [],
        "choices": [],
        "answer": 48,
        "acceptedAnswers": ["48"],
        "explanation": (
            "The correct answer is 48. It's given that in the xy-plane, when the graph of the function f, where "
            "y = f(x), is shifted up 6 units, the resulting graph is defined by the function g. Therefore, function g "
            "can be defined by the equation g(x) = f(x) + 6. It's given that f(x) = (x - 1)(x + 3)(x - 2). Substituting "
            "(x - 1)(x + 3)(x - 2) for f(x) in the equation g(x) = f(x) + 6 yields "
            "g(x) = (x - 1)(x + 3)(x - 2) + 6. For the point (4, b), the value of x is 4. Substituting 4 for x in the "
            "equation g(x) = (x - 1)(x + 3)(x - 2) + 6 yields g(4) = (4 - 1)(4 + 3)(4 - 2) + 6, or g(4) = 48. It follows "
            "that the graph of y = g(x) crosses through the point (4, 48). Therefore, the value of b is 48."
        ),
    },
    "f89af023": {
        "prompt": (
            "A rectangular volleyball court has an area of 162 square meters. If the length of the court is twice the "
            "width, what is the width of the court, in meters?"
        ),
        "equations": [],
        "choices": [
            {"text": "9"},
            {"text": "18"},
            {"text": "27"},
            {"text": "54"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. Let w represent the width, in meters, of the court. Since the length of the court is "
            "twice the width, the length is 2w meters. The area of a rectangle is the product of its length and width, so "
            "2w · w = 162, or 2w^2 = 162. Dividing both sides by 2 yields w^2 = 81. Taking the positive square root yields "
            "w = 9. Therefore, the width of the court is 9 meters.\n\n"
            "Choice B is incorrect. This is the length of the court, not the width.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "4a0d0399": {
        "prompt": (
            "The function f is defined by f(x) = a^x + b, where a and b are constants. In the xy-plane, the graph of "
            "y = f(x) has an x-intercept at (2, 0) and a y-intercept at (0, -323). What is the value of b?"
        ),
        "equations": [],
        "choices": [],
        "answer": -324,
        "acceptedAnswers": ["-324"],
        "explanation": (
            "The correct answer is -324. It's given that the function f is defined by f(x) = a^x + b, where a and b are "
            "constants. It's also given that the graph of y = f(x) has a y-intercept at (0, -323). It follows that "
            "f(0) = -323. Substituting 0 for x and -323 for f(x) in f(x) = a^x + b yields -323 = a^0 + b, or "
            "-323 = 1 + b. Subtracting 1 from each side of this equation yields -324 = b. Therefore, the value of b is "
            "-324."
        ),
    },
    "b4a6ed81": {
        "prompt": (
            "The expression 90y^5 - 54y^4 is equivalent to ry^4(15y - 9), where r is a constant. What is the value of r?"
        ),
        "equations": [],
        "choices": [],
        "answer": 6,
        "acceptedAnswers": ["6"],
        "explanation": (
            "The correct answer is 6. Applying the distributive property to the expression ry^4(15y - 9) yields "
            "15ry^5 - 9ry^4. Since 90y^5 - 54y^4 is equivalent to ry^4(15y - 9), it follows that 90y^5 - 54y^4 is also "
            "equivalent to 15ry^5 - 9ry^4. Since these expressions are equivalent, it follows that corresponding "
            "coefficients are equivalent. Therefore, 15r = 90 and -9r = -54. Solving either of these equations for r "
            "yields r = 6."
        ),
    },
    "34847f8a": {
        "prompt": (
            "2/(x - 2) + 3/(x + 5) = (rx + t)/((x - 2)(x + 5))\n"
            "The equation above is true for all x > 2, where r and t are positive constants. What is the value of rt?"
        ),
        "equations": [],
        "choices": [
            {"text": "-20"},
            {"text": "15"},
            {"text": "20"},
            {"text": "60"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. Combining the fractions on the left-hand side of the given equation over the common "
            "denominator (x - 2)(x + 5) yields [2(x + 5) + 3(x - 2)]/[(x - 2)(x + 5)], which is equivalent to "
            "(2x + 10 + 3x - 6)/[(x - 2)(x + 5)], or (5x + 4)/[(x - 2)(x + 5)]. Since the equation is true for all x > 2, "
            "it follows that rx + t = 5x + 4. Therefore, r = 5 and t = 4, so rt = 20.\n\n"
            "Choice A is incorrect and may result from a sign error.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice D is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "263f9937": {
        "prompt": (
            "A culture of bacteria is growing at an exponential rate, as shown in the table above. At this rate, on "
            "which day would the number of bacteria per milliliter reach 5.12 × 10^8?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/263f9937.jpg",
        "choices": [
            {"text": "Day 5"},
            {"text": "Day 9"},
            {"text": "Day 11"},
            {"text": "Day 12"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. The number of bacteria per milliliter is doubling each day. For example, from day 1 to "
            "day 2, the number of bacteria increased from 2.5 × 10^5 to 5.0 × 10^5. At the end of day 3 there are 10^6 "
            "bacteria per milliliter. At the end of day 4, there will be 10^6 × 2 bacteria per milliliter. At the end of "
            "day 5, there will be (10^6 × 2) × 2, or 10^6 × (2^2) bacteria per milliliter, and so on. At the end of day d, "
            "the number of bacteria will be 10^6 × (2^(d - 3)). If the number of bacteria per milliliter will reach "
            "5.12 × 10^8 at the end of day d, then the equation 10^6 × (2^(d - 3)) = 5.12 × 10^8 must hold. Since "
            "5.12 × 10^8 can be rewritten as 512 × 10^6, the equation is equivalent to 2^(d - 3) = 512. Rewriting 512 as "
            "2^9 gives d - 3 = 9, so d = 12. The number of bacteria per milliliter would reach 5.12 × 10^8 at the end of "
            "day 12.\n\n"
            "Choice A is incorrect. Given the growth rate of the bacteria, the number of bacteria will not reach "
            "5.12 × 10^8 per milliliter by the end of day 5.\n\n"
            "Choice B is incorrect. Given the growth rate of the bacteria, the number of bacteria will not reach "
            "5.12 × 10^8 per milliliter by the end of day 9.\n\n"
            "Choice C is incorrect. Given the growth rate of the bacteria, the number of bacteria will not reach "
            "5.12 × 10^8 per milliliter by the end of day 11."
        ),
    },
    "926c246b": {
        "prompt": (
            "D = 5,640(1.9)^t\n"
            "The equation above estimates the global data traffic D, in terabytes, for the year that is t years after "
            "2010. What is the best interpretation of the number 5,640 in this context?"
        ),
        "equations": [],
        "choices": [
            {"text": "The estimated amount of increase of data traffic, in terabytes, each year"},
            {"text": "The estimated percent increase in the data traffic, in terabytes, each year"},
            {"text": "The estimated data traffic, in terabytes, for the year that is t years after 2010"},
            {"text": "The estimated data traffic, in terabytes, in 2010"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. Since t represents the number of years after 2010, the estimated data traffic, in "
            "terabytes, in 2010 can be calculated using the given equation when t = 0. Substituting 0 for t in the given "
            "equation yields D = 5,640(1.9)^0, or 5,640(1) = 5,640. Thus, 5,640 represents the estimated data traffic, in "
            "terabytes, in 2010.\n\n"
            "Choice A is incorrect. Since the equation is exponential, the amount of increase of data traffic each year "
            "isn't constant.\n\n"
            "Choice B is incorrect. According to the equation, the percent increase in data traffic each year is 90%.\n\n"
            "Choice C is incorrect. The estimated data traffic, in terabytes, for the year that is t years after 2010 is "
            "represented by D, not the number 5,640."
        ),
    },
    "137cc6fd": {
        "prompt": (
            "(70n)^(1/5)((70n)^(1/6))^2\n"
            "For what value of x is the given expression equivalent to (70n)^(30x), where n > 1?"
        ),
        "equations": [],
        "choices": [],
        "answer": "4/225",
        "acceptedAnswers": ["4/225", ".0177", ".0178", "0.0177", "0.0178", "0.017", "0.018"],
        "explanation": (
            "The correct answer is 4/225. The given expression can be rewritten using rational exponents as "
            "(70n)^(1/5) · ((70n)^(1/6))^2. Applying the power rule yields (70n)^(1/5) · (70n)^(2/6), or "
            "(70n)^(1/5) · (70n)^(1/3). Applying the product rule for exponents with the same base yields "
            "(70n)^(1/5 + 1/3) = (70n)^(3/15 + 5/15) = (70n)^(8/15). Setting this equal to (70n)^(30x) yields "
            "30x = 8/15, so x = 8/(15 · 30) = 8/450 = 4/225. Note that 4/225, .0177, and .0178 are examples of ways to "
            "enter a correct answer."
        ),
    },
    "cc2601cb": {
        "prompt": "The x-intercept of the graph shown is (x, 0). What is the value of x?",
        "equations": [],
        "figure": "/qbank/math/figures/cc2601cb.jpg",
        "choices": [],
        "answer": 7,
        "acceptedAnswers": ["7"],
        "explanation": (
            "The correct answer is 7. It's given that the x-intercept of the graph shown is (x, 0). The graph passes "
            "through the point (7, 0). Therefore, the value of x is 7."
        ),
    },
    "6bdcac03": {
        "prompt": (
            "x^2 = -841\n"
            "How many distinct real solutions does the given equation have?"
        ),
        "equations": [],
        "choices": [
            {"text": "Exactly one"},
            {"text": "Exactly two"},
            {"text": "Infinitely many"},
            {"text": "Zero"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. Since the square of a real number is never negative, the given equation isn't true for "
            "any real value of x. Therefore, the given equation has zero distinct real solutions.\n\n"
            "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
            "Choice C is incorrect and may result from conceptual or calculation errors."
        ),
    },
    "f5aa5040": {
        "prompt": (
            "In the xy-plane, a line with equation 2y = c for some constant c intersects a parabola at exactly one "
            "point. If the parabola has equation y = -2x^2 + 9x, what is the value of c?"
        ),
        "equations": [],
        "choices": [],
        "answer": 20.25,
        "acceptedAnswers": ["20.25", "81/4"],
        "explanation": (
            "The correct answer is 81/4. The given linear equation is 2y = c. Dividing both sides of this equation by 2 "
            "yields y = c/2. Substituting c/2 for y in the equation of the parabola yields c/2 = -2x^2 + 9x. Adding 2x^2 "
            "and -9x to both sides of this equation yields 2x^2 - 9x + c/2 = 0. Since it's given that the line and the "
            "parabola intersect at exactly one point, the equation 2x^2 - 9x + c/2 = 0 must have exactly one solution. An "
            "equation of the form Ax^2 + Bx + C = 0, where A, B, and C are constants, has exactly one solution when the "
            "discriminant, B^2 - 4AC, is equal to 0. In the equation 2x^2 - 9x + c/2 = 0, where A = 2, B = -9, and "
            "C = c/2, the discriminant is (-9)^2 - 4(2)(c/2). Setting the discriminant equal to 0 yields "
            "(-9)^2 - 4(2)(c/2) = 0, or 81 - 4c = 0. Adding 4c to both sides of this equation yields 81 = 4c. Dividing "
            "both sides of this equation by 4 yields c = 81/4. Note that 81/4 and 20.25 are examples of ways to enter a "
            "correct answer."
        ),
    },
    "7f2524bf": {
        "prompt": (
            "The graph shown gives the estimated value, in dollars, of a tablet as a function of the number of months "
            "since it was purchased. What is the best interpretation of the y-intercept of the graph in this context?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/7f2524bf.jpg",
        "choices": [
            {"text": "The estimated value of the tablet was $225 when it was purchased."},
            {"text": "The estimated value of the tablet 24 months after it was purchased was $225."},
            {"text": "The estimated value of the tablet had decreased by $225 in the 24 months after it was purchased."},
            {"text": "The estimated value of the tablet decreased by approximately 2.25% each year after it was purchased."},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. It's given that the graph shown gives the estimated value y, in dollars, of a tablet "
            "as a function of the number of months since it was purchased, x. The y-intercept of a graph is the point at "
            "which the graph intersects the y-axis, or when x is 0. The graph shown intersects the y-axis at the point "
            "(0, 225). It follows that 0 months after the tablet was purchased, or when the tablet was purchased, the "
            "estimated value of the tablet was 225 dollars. Therefore, the best interpretation of the y-intercept is that "
            "the estimated value of the tablet was $225 when it was purchased.\n\n"
            "Choice B is incorrect. The estimated value of the tablet 24 months after it was purchased was $50, not "
            "$225.\n\n"
            "Choice C is incorrect. The estimated value of the tablet had decreased by $225 - $50, or $175, not $225, in "
            "the 24 months after it was purchased.\n\n"
            "Choice D is incorrect and may result from conceptual errors."
        ),
    },
    "4fbffc0a": {
        "prompt": (
            "The graph shows the height above ground, in meters, of a ball x seconds after the ball was launched upward "
            "from a platform. Which statement is the best interpretation of the marked point (1.0, 4.8) in this context?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/4fbffc0a.jpg",
        "choices": [
            {"text": "1.0 second after being launched, the ball's height above ground is 4.8 meters."},
            {"text": "4.8 seconds after being launched, the ball's height above ground is 1.0 meter."},
            {"text": "The ball was launched from an initial height of 1.0 meter with an initial velocity of 4.8 meters per second."},
            {"text": "The ball was launched from an initial height of 4.8 meters with an initial velocity of 1.0 meter per second."},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. It's given that the graph shows the height above ground, in meters, of a ball x seconds "
            "after the ball was launched upward from a platform. In the graph shown, the x-axis represents time, in "
            "seconds, and the y-axis represents the height of the ball above ground, in meters. It follows that for the "
            "marked point (1.0, 4.8), 1.0 represents the time, in seconds, after the ball was launched upward from a "
            "platform and 4.8 represents the height of the ball above ground, in meters. Therefore, the best "
            "interpretation of the marked point (1.0, 4.8) is 1.0 second after being launched, the ball's height above "
            "ground is 4.8 meters.\n\n"
            "Choice B is incorrect and may result from conceptual errors.\n\n"
            "Choice C is incorrect and may result from conceptual errors.\n\n"
            "Choice D is incorrect and may result from conceptual errors."
        ),
    },
    "1d3c5c95": {
        "prompt": (
            "f(x) = 4,000(0.75)^x\n"
            "An entomologist recommended a program to reduce a certain invasive beetle population in an area. The given "
            "function estimates this beetle species' population x years after 2012, where x ≤ 7. Which of the following "
            "is the best interpretation of 4,000 in this context?"
        ),
        "equations": [],
        "choices": [
            {"text": "The estimated initial beetle population for this species and area in 2012"},
            {"text": "The estimated beetle population for this species and area 7 years after 2012"},
            {"text": "The estimated percent decrease in the beetle population for this species and area each year after 2012"},
            {"text": "The estimated percent decrease in the beetle population for this species and area every 7 years after 2012"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. For an exponential function in the form f(x) = a(b)^x, where a and b are positive "
            "constants and b < 1, the initial value of f(x), or the value of f(x) when x = 0, is a and the value of f(x) "
            "decreases by 100(1 - b)% each time x increases by 1. Therefore, the initial value of the function "
            "f(x) = 4,000(0.75)^x, or the value of f(x) when x = 0, is 4,000. Therefore, the best interpretation of 4,000 "
            "in this context is the estimated initial beetle population for this species and area in 2012.\n\n"
            "Choice B is incorrect. The estimated beetle population for this species and area 7 years after 2012 is "
            "4,000(0.75)^7, or approximately 534, not 4,000.\n\n"
            "Choice C is incorrect. The estimated percent decrease in the beetle population for this species and area "
            "each year after 2012 is 100(1 - 0.75), or 25, not 4,000.\n\n"
            "Choice D is incorrect. The estimated percent decrease in the beetle population for this species and area "
            "every 7 years after 2012 is 100(1 - 0.75^7), or approximately 87, not 4,000."
        ),
    },
    "9654add7": {
        "prompt": (
            "f(x) = -500x^2 + 25,000x\n"
            "The revenue f(x), in dollars, that a company receives from sales of a product is given by the function f "
            "above, where x is the unit price, in dollars, of the product. The graph of y = f(x) in the xy-plane "
            "intersects the x-axis at 0 and a. What does a represent?"
        ),
        "equations": [],
        "choices": [
            {"text": "The revenue, in dollars, when the unit price of the product is $0"},
            {"text": "The unit price, in dollars, of the product that will result in maximum revenue"},
            {"text": "The unit price, in dollars, of the product that will result in a revenue of $0"},
            {"text": "The maximum revenue, in dollars, that the company can make"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. By definition, the y-value when a function intersects the x-axis is 0. It's given that "
            "the graph of the function intersects the x-axis at 0 and a, that x is the unit price, in dollars, of a "
            "product, and that f(x), where y = f(x), is the revenue, in dollars, that a company receives from the sales "
            "of the product. Since the value of a occurs when y = 0, a is the unit price, in dollars, of the product that "
            "will result in a revenue of $0.\n\n"
            "Choice A is incorrect. The revenue, in dollars, when the unit price of the product is $0 is represented by "
            "f(x), when x = 0.\n\n"
            "Choice B is incorrect. The unit price, in dollars, of the product that will result in maximum revenue is "
            "represented by the x-coordinate of the maximum of f.\n\n"
            "Choice D is incorrect. The maximum revenue, in dollars, that the company can make is represented by the "
            "y-coordinate of the maximum of f."
        ),
    },
    "4618501a": {
        "prompt": (
            "f(x) = 3,000(0.75)^x\n"
            "A conservation scientist implemented a program to reduce the population of a certain species in an area. "
            "The given function estimates this species' population x years after 2008, where x ≤ 8. Which of the "
            "following is the best interpretation of 3,000 in this context?"
        ),
        "equations": [],
        "choices": [
            {"text": "The estimated percent decrease in the population for this species and area every 8 years after 2008"},
            {"text": "The estimated percent decrease in the population for this species and area each year after 2008"},
            {"text": "The estimated population for this species and area 8 years after 2008"},
            {"text": "The estimated initial population for this species and area in 2008"},
        ],
        "answer": 3,
        "explanation": (
            "Choice D is correct. Substituting 0 for x in the given equation yields f(0) = 3,000(0.75)^0, which is "
            "equivalent to f(0) = 3,000(1), or f(0) = 3,000. It's given that the function estimates the species' "
            "population x years after 2008, so it follows that the estimated population of the species is 3,000 in 2008. "
            "Therefore, the best interpretation of 3,000 in this context is the estimated initial population for this "
            "species and area in 2008.\n\n"
            "Choice A is incorrect and may result from conceptual errors.\n\n"
            "Choice B is incorrect. The estimated percent decrease in the population for this species and area each year "
            "after 2008 is 25%, not 3,000.\n\n"
            "Choice C is incorrect. The estimated population for this species and area 8 years after 2008 is "
            "3,000(0.75)^8, or approximately 300, not 3,000."
        ),
    },
    # Verify-list patches (only where current JSON still mismatches PDF)
    "beca03de": {
        "prompt": (
            "y = (15w)(w)\n"
            "A rectangle has a length that is 15 times its width. The function above represents this situation, where y "
            "is the area, in square feet, of the rectangle and y > 0. Which of the following is the best interpretation "
            "of 15w in this context?"
        ),
        "equations": [],
        "choices": [
            {"text": "The length of the rectangle, in feet"},
            {"text": "The area of the rectangle, in square feet"},
            {"text": "The difference between the length and the width of the rectangle, in feet"},
            {"text": "The width of the rectangle, in feet"},
        ],
        "answer": 0,
        "explanation": (
            "Choice A is correct. It's given that a rectangle has a length that is 15 times its width. It's also given "
            "that the function y = (15w)(w) represents this situation, where y is the area, in square feet, of the "
            "rectangle and y > 0. The area of a rectangle can be calculated by multiplying the rectangle's length by its "
            "width. Since the rectangle has a length that is 15 times its width, it follows that w represents the width "
            "of the rectangle, in feet, and 15w represents the length of the rectangle, in feet. Therefore, the best "
            "interpretation of 15w in this context is that it's the length of the rectangle, in feet.\n\n"
            "Choice B is incorrect. This is the best interpretation of y, not 15w, in the given function.\n\n"
            "Choice C is incorrect and may result from conceptual errors.\n\n"
            "Choice D is incorrect. This is the best interpretation of w, not 15w, in the given function."
        ),
    },
    "a5663025": {
        "prompt": (
            "A system of equations consists of a quadratic equation and a linear equation. The equations in this system "
            "are graphed in the xy-plane above. How many solutions does this system have?"
        ),
        "equations": [],
        "figure": "/qbank/math/figures/a5663025.jpg",
        "choices": [
            {"text": "0"},
            {"text": "1"},
            {"text": "2"},
            {"text": "3"},
        ],
        "answer": 2,
        "explanation": (
            "Choice C is correct. The solutions to a system of two equations correspond to points where the graphs of "
            "the equations intersect. The given graphs intersect at 2 points; therefore, the system has 2 solutions.\n\n"
            "Choice A is incorrect because the graphs intersect.\n\n"
            "Choice B is incorrect because the graphs intersect more than once.\n\n"
            "Choice D is incorrect. It's not possible for the graph of a quadratic equation and the graph of a linear "
            "equation to intersect at more than 2 points."
        ),
    },
    "301faf80": {
        "prompt": (
            "The product of two positive integers is 462. If the first integer is 5 greater than twice the second "
            "integer, what is the smaller of the two integers?"
        ),
        "equations": [],
        "choices": [],
        "answer": 14,
        "acceptedAnswers": ["14"],
        "explanation": (
            "The correct answer is 14. Let x represent the first integer and y represent the second integer. If the first "
            "integer is 5 greater than twice the second integer, then x = 2y + 5. It's given that the product of the two "
            "integers is 462; therefore xy = 462. Substituting 2y + 5 for x in this equation yields (2y + 5)(y) = 462, "
            "which can be written as 2y^2 + 5y = 462. Subtracting 462 from each side of this equation yields "
            "2y^2 + 5y - 462 = 0. The left-hand side of this equation can be factored by finding two values whose product "
            "is 2(-462), or -924, and whose sum is 5. The two values whose product is -924 and whose sum is 5 are 33 and "
            "-28. Thus, the equation 2y^2 + 5y - 462 = 0 can be rewritten as 2y^2 - 28y + 33y - 462 = 0, which is "
            "equivalent to 2y(y - 14) + 33(y - 14) = 0, or (2y + 33)(y - 14) = 0. By the zero product property, it follows "
            "that 2y + 33 = 0 or y - 14 = 0. Subtracting 33 from both sides of the equation 2y + 33 = 0 yields 2y = -33. "
            "Dividing both sides of this equation by 2 yields y = -33/2. Since y is a positive integer, the value of y "
            "isn't -33/2. Adding 14 to both sides of the equation y - 14 = 0 yields y = 14. Substituting 14 for y in the "
            "equation xy = 462 yields x(14) = 462. Dividing both sides of this equation by 14 yields x = 33. Therefore, "
            "the two integers are 14 and 33, so the smaller of the two integers is 14."
        ),
    },
}
