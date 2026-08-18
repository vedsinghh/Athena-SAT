#!/usr/bin/env python3
"""Post-pass repairs for Educator Bank Algebra.

Policy: equations and symbolic choices are text (KaTeX). Images are only for
graphs, figures, and tables the bank cannot expose as text.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import fitz  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from extract_questions import MATH_CHOICE_IMG, MATH_FIG, crop_math_figure, render_clip  # noqa: E402

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Algebra 1.pdf")
DATA = ROOT / "src" / "data" / "mathQuestions.json"


def page_for(bank: fitz.Document, qid: str) -> fitz.Page:
    return next(p for p in bank if qid in (p.get_text() or ""))


def render_table(headers: list[str], rows: list[list[str]], path: Path, scale: int = 3) -> None:
    pad, col_w, row_h = 16, 90, 36
    w = pad * 2 + col_w * len(headers)
    h = pad * 2 + row_h * (len(rows) + 1)
    img = Image.new("RGB", (w * scale, h * scale), "white")
    d = ImageDraw.Draw(img)
    S = lambda x: x * scale  # noqa: E731
    try:
        font = ImageFont.truetype(
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf", 15 * scale
        )
        font_h = ImageFont.truetype(
            "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", 15 * scale
        )
    except Exception:
        font = font_h = ImageFont.load_default()
    x0 = y0 = pad
    for i in range(len(rows) + 2):
        y = y0 + i * row_h
        d.line(
            [(S(x0), S(y)), (S(x0 + col_w * len(headers)), S(y))],
            fill="black",
            width=max(1, scale // 2),
        )
    for j in range(len(headers) + 1):
        x = x0 + j * col_w
        d.line(
            [(S(x), S(y0)), (S(x), S(y0 + row_h * (len(rows) + 1)))],
            fill="black",
            width=max(1, scale // 2),
        )
    for j, htext in enumerate(headers):
        bbox = d.textbbox((0, 0), htext, font=font_h)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(
            (S(x0 + j * col_w + col_w / 2) - tw / 2, S(y0 + row_h / 2) - th / 2),
            htext,
            fill="black",
            font=font_h,
        )
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            text = str(val)
            bbox = d.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            d.text(
                (
                    S(x0 + j * col_w + col_w / 2) - tw / 2,
                    S(y0 + (i + 1) * row_h + row_h / 2) - th / 2,
                ),
                text,
                fill="black",
                font=font,
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=95)


# Summer-style text equations (no {{eq:}} image slots).
TEXT_FIXES: dict[str, dict] = {
    "edc1b7b7": {
        "prompt": '2(8x) + 4(7y) = 12\n-2(8x) + 4(7y) = 12\nThe solution to the given system of equations is (x, y). What is the value of 8x + 7y?',
        "equations": [],
        "choices": [],
        "answer": '3',
        "acceptedAnswers": [
            '3'
        ]
    },
    "ac472881": {
        "prompt": '(12x + 28)/4 - s/13 = r(x - 8)\nIn the given equation, s and r are constants, and s > 0. If the equation has infinitely many solutions, what is the value of s?',
        "equations": [],
        "choices": [],
        "answer": '403',
        "acceptedAnswers": [
            '403'
        ]
    },
    "002dba45": {
        "prompt": 'y = (-17/3)x + 5\nLine k is defined by the given equation. Line j is perpendicular to line k in the xy-plane. What is the slope of line j?',
        "equations": [],
        "choices": [],
        "answer": '3/17',
        "acceptedAnswers": [
            '3/17',
            '.1764',
            '.1765',
            '0.1764',
            '0.1765'
        ]
    },
    "fa80893a": {
        "prompt": 'If 2x + 3 = 9, what is the value of 6x - 1?',
        "equations": [],
        "choices": [],
        "answer": '17',
        "acceptedAnswers": [
            '17'
        ]
    },
    "3008cfc3": {
        "prompt": 'The table gives the coordinates of two points on a line in the xy-plane. The y-intercept of the line is (k - 5, b), where\nk\nand b are constants. What is the value of b?',
        "choices": [],
        "answer": '33',
        "acceptedAnswers": [
            '33'
        ],
        "figure": '/qbank/math/figures/3008cfc3.jpg',
        "explanation": "The correct answer is 33. It's given in the table that the coordinates of two points on a line in the xy-plane are (k, 13) and (k + 7, -15). The slope m between these points is m = (-15 - 13)/((k + 7) - k) = (-28)/7 = -4. It's given that the y-intercept of the line is (k - 5, b). Using the points (k - 5, b) and (k, 13) with slope -4 gives -4 = (13 - b)/(k - (k - 5)) = (13 - b)/5. Multiplying both sides by 5 yields -20 = 13 - b. Subtracting 13 from both sides yields -33 = -b, so b = 33."
    },
    "d1b66ae6": {
        "prompt": '-x + y = -3.5\nx + 3y = 9.5\nIf (x, y) satisfies the system of equations above, what is the value of y?',
        "equations": [],
        "choices": [],
        "answer": '1.5',
        "acceptedAnswers": [
            '1.5',
            '3/2',
            '1.50'
        ]
    },
    "3409707e": {
        "prompt": 'x + y = 125\nx + 2y = 155\nThe solution to the given system of equations is (x, y). What is the value of y?',
        "equations": [],
        "choices": [],
        "answer": '30',
        "acceptedAnswers": [
            '30'
        ]
    },
    "00723d16": {
        "prompt": '3y + 12x = 5\nLine ℓ is defined by the given equation. Line n is perpendicular to line ℓ in the xy-plane. What is the slope of line n?',
        "equations": [],
        "choices": [],
        "answer": '1/4',
        "acceptedAnswers": [
            '1/4',
            '0.25',
            '.25'
        ],
        "explanation": 'The correct answer is 1/4. For an equation in slope-intercept form y = mx + b, m represents the slope of the line. Line ℓ is defined by 3y + 12x = 5. Subtracting 12x from both sides yields 3y = -12x + 5. Dividing both sides by 3 yields y = -4x + 5/3. Therefore, the slope of line ℓ is -4. Line n is perpendicular to line ℓ, so the slope of line n is the negative reciprocal of -4, which is 1/4.'
    },
    "ff501705": {
        "prompt": '(3/2)y - (1/4)x = 2/3 - (3/2)y\n(1/2)x + 3/2 = py + 9/2\nIn the given system of equations, p is a constant. If the system has no solution, what is the value of p?',
        "equations": [],
        "choices": [],
        "answer": '6',
        "acceptedAnswers": [
            '6'
        ]
    },
    "e25f0807": {
        "prompt": 'The table shows two values of x and their corresponding values of y. The graph of the linear equation representing this relationship passes through the point (1/4, a). What is the value of a?',
        "equations": [],
        "choices": [],
        "answer": '16.25',
        "acceptedAnswers": [
            '16.25',
            '65/4'
        ],
        "figure": '/qbank/math/figures/e25f0807.jpg'
    },
    "686b7244": {
        "prompt": '10x + 15y = 85\nA certain apprentice has enrolled in 85 hours of training courses. The equation shown represents this situation, where x is the number of on-site training courses and y is the number of online training courses this apprentice has enrolled in. How many more hours does each online training course take than each on-site training course?',
        "equations": [],
        "choices": [],
        "answer": '5',
        "acceptedAnswers": [
            '5'
        ]
    },
    "e62cfe5f": {
        "prompt": 'According to a model, the head width, in millimeters, of a worker bumblebee can be estimated by adding 0.6 to four times the body weight of the bee, in grams. According to the model, what would be the head width, in millimeters, of a worker bumblebee that has a body weight of 0.5 grams?',
        "equations": [],
        "choices": [],
        "answer": '2.6',
        "acceptedAnswers": [
            '2.6',
            '13/5'
        ]
    },
    "465c73ad": {
        "prompt": '10x = 86\nWhat value of x is the solution to the given equation?',
        "equations": [],
        "choices": [],
        "answer": '8.6',
        "acceptedAnswers": [
            '8.6',
            '43/5'
        ]
    },
    "db422e7f": {
        "prompt": '4y + 8x = 6\nLine p is defined by the given equation. Line r is perpendicular to line p in the xy-plane. What is the slope of line r?',
        "equations": [],
        "choices": [],
        "answer": '1/2',
        "acceptedAnswers": [
            '1/2',
            '0.5',
            '.5'
        ]
    },
    "7fac16fb": {
        "prompt": 'The function f is defined by f(x) = (7/10)x + 55. What is the value of f(20)?',
        "equations": [],
        "choices": [],
        "answer": '69',
        "acceptedAnswers": [
            '69'
        ]
    },
    "f2b63f49": {
        "prompt": '8x - 7x + 130 = 260\nWhat value of x is the solution to the given equation?',
        "equations": [],
        "choices": [],
        "answer": '130',
        "acceptedAnswers": [
            '130'
        ]
    },
    "e3cf671f": {
        "prompt": 'The function f is defined by f(x) = 4x + k(x - 1), where k is a constant, and f(5) = 32. What is the value of f(10)?',
        "equations": [],
        "choices": [],
        "answer": '67',
        "acceptedAnswers": [
            '67'
        ]
    },
    "571174f3": {
        "prompt": '(2/5)x + (7/5)y = 2/7\ngx + ky = 5/2\nIn the given system of equations, g and k are constants. The system has infinitely many solutions. What is the value of g/k?',
        "equations": [],
        "choices": [],
        "answer": '2/7',
        "acceptedAnswers": [
            '2/7',
            '.2857',
            '0.2857',
            '0.285',
            '0.286'
        ]
    },
    "0b332f00": {
        "prompt": 'The function g is defined by g(x) = 6x. For what value of x is g(x) = 54?',
        "choices": [],
        "answer": '9',
        "acceptedAnswers": [
            '9'
        ]
    },
    "349a5bc1": {
        "prompt": '4x + 5 = 165\nWhat is the solution to the given equation?',
        "equations": [],
        "choices": [],
        "answer": '40',
        "acceptedAnswers": [
            '40'
        ]
    },
    "4f1342d6": {
        "prompt": 'In August, a car dealer completed 15 more than 3 times the number of sales the car dealer completed in\nSeptember. In August and September, the car dealer completed 363 sales. How many sales did the car dealer\ncomplete in September?',
        "choices": [],
        "answer": '87',
        "acceptedAnswers": [
            '87'
        ]
    },
    "447fa970": {
        "prompt": 'The function f is defined by the equation f(x) = 7x + 2. What is the value of f(x) when x = 4?',
        "choices": [],
        "answer": '30',
        "acceptedAnswers": [
            '30'
        ]
    },
    "4edecdba": {
        "prompt": '8x + 11y = 170\nThe equation gives the possible combinations of the number of 2009 premium grade Log Cabin Pennies, x, and the number of 1996 select grade Lincoln Pennies, y, in a collection that is worth a total of $170. If there are 6 1996 select grade Lincoln Pennies in the collection, how many 2009 premium grade Log Cabin Pennies are in the collection?',
        "equations": [],
        "choices": [],
        "answer": '13',
        "acceptedAnswers": [
            '13'
        ]
    },
    "1087f6c4": {
        "prompt": '24.5x + 24.75y = 641\nIsabel ordered topsoil and crushed stone, which cost a total of $641, for her garden. The given equation represents the relationship between the number of cubic yards of topsoil, x, and the number of tons of crushed stone, y, Isabel ordered. How much more, in dollars, did a ton of crushed stone cost Isabel than a cubic yard of topsoil?',
        "equations": [],
        "choices": [],
        "answer": '0.25',
        "acceptedAnswers": [
            '0.25',
            '1/4',
            '.25'
        ]
    },
    "b5f62071": {
        "prompt": '48x - 64y = 48y + 24\nry = 1/8 - 12x\nIn the given system of equations, r is a constant. If the system has no solution, what is the value of r?',
        "equations": [],
        "choices": [],
        "answer": '-28',
        "acceptedAnswers": [
            '-28'
        ]
    },
    "c1bd5301": {
        "prompt": 'A model predicts that a certain animal weighed 241 pounds when it was born and that the animal gained 3 pounds per day in its first year of life. This model is defined by an equation in the form f(x) = a + bx, where f(x) is the predicted weight, in pounds, of the animal x days after it was born, and a and b are constants. What is the value of a?',
        "equations": [],
        "choices": [],
        "answer": '241',
        "acceptedAnswers": [
            '241'
        ]
    },
    "5c94e6fa": {
        "prompt": '3x + 21 = 3x + k\nIn the given equation, k is a constant. The equation has infinitely many solutions. What is the value of k?',
        "equations": [],
        "choices": [],
        "answer": '21',
        "acceptedAnswers": [
            '21'
        ]
    },
    "7625073d": {
        "prompt": 'The equation 7g + 7b = 840 represents the number of blue tiles, b, and the number of green tiles, g, an artist needs\nfor an 840-square-inch tile project. The artist needs 71 blue tiles for the project. How many green tiles does he\nneed?',
        "choices": [],
        "answer": '49',
        "acceptedAnswers": [
            '49'
        ]
    },
    "c5e38487": {
        "prompt": 'A chemist combines water and acetic acid to make a mixture with a volume of 56 milliliters (mL). The volume of\nacetic acid in the mixture is 10 mL. What is the volume of water, in mL, in the mixture? (Assume that the volume of\nthe mixture is the sum of the volumes of water and acetic acid before they were mixed.)',
        "choices": [],
        "answer": '46',
        "acceptedAnswers": [
            '46'
        ]
    },
    "15daa8d6": {
        "prompt": '2x + 16 = a(x + 8)\nIn the given equation, a is a constant. If the equation has infinitely many solutions, what is the value of a?',
        "equations": [],
        "choices": [],
        "answer": '2',
        "acceptedAnswers": [
            '2'
        ]
    },
    "2f0a43b2": {
        "prompt": 'If x/8 = 5, what is the value of 8/x?',
        "equations": [],
        "choices": [],
        "answer": '.2',
        "acceptedAnswers": [
            '.2',
            '0.2',
            '1/5'
        ]
    },
    "bd9eb2b5": {
        "prompt": 'The function f is defined by f(x) = 8x. For what value of x does f(x) = 72?',
        "equations": [],
        "choices": [
            {
                "text": '8'
            },
            {
                "text": '9'
            },
            {
                "text": '64'
            },
            {
                "text": '80'
            }
        ],
        "answer": 1,
        "explanation": 'Choice B is correct. Substituting 72 for f(x) in the given function yields 72 = 8x. Dividing each side of this equation by 8 yields x = 9. Therefore, f(x) = 72 when x = 9.\n\nChoice A is incorrect. This is the value of x for which f(x) = 64, not f(x) = 72.\n\nChoice C is incorrect. This is the value of x for which f(x) = 512, not f(x) = 72.\n\nChoice D is incorrect. This is the value of x for which f(x) = 640, not f(x) = 72.'
    },
    "b0fc3166": {
        "prompt": 'The graph of a system of linear equations is shown. What is the solution (x, y) to the system?',
        "equations": [],
        "choices": [
            {
                "text": '(0, 3)'
            },
            {
                "text": '(1, 3)'
            },
            {
                "text": '(2, 3)'
            },
            {
                "text": '(3, 3)'
            }
        ],
        "answer": 2,
        "figure": '/qbank/math/figures/b0fc3166.jpg'
    },
    "9bbce683": {
        "prompt": 'For line h, the table shows three values of x and their corresponding values of y. Line k is the result of translating line h down 5 units in the xy-plane. What is the x-intercept of line k?',
        "equations": [],
        "choices": [
            {
                "text": '(-26/3, 0)'
            },
            {
                "text": '(-9/2, 0)'
            },
            {
                "text": '(-11/3, 0)'
            },
            {
                "text": '(-17/6, 0)'
            }
        ],
        "answer": 3,
        "figure": '/qbank/math/figures/9bbce683.jpg'
    },
    "1480dd5c": {
        "prompt": 'f(x) = 4x + b\nFor the linear function f, b is a constant and f(7) = 28. What is the value of b?',
        "equations": [],
        "choices": [
            {
                "text": '0'
            },
            {
                "text": '1'
            },
            {
                "text": '4'
            },
            {
                "text": '7'
            }
        ],
        "answer": 0,
        "explanation": "Choice A is correct. For the linear function f, it's given that f(7) = 28. Substituting 7 for x and 28 for f(x) in f(x) = 4x + b yields 28 = 4(7) + b, or 28 = 28 + b. Subtracting 28 from each side yields b = 0.\n\nChoice B is incorrect. Substituting b = 1 yields f(7) = 28 + 1 = 29, not 28.\n\nChoice C is incorrect. Substituting b = 4 yields f(7) = 28 + 4 = 32, not 28.\n\nChoice D is incorrect. Substituting b = 7 yields f(7) = 28 + 7 = 35, not 28."
    },
    "0d6ab461": {
        "prompt": 'Gabriella deposits $35 in a savings account at the end of each week. At the beginning of the 1st week of a year there was $600 in that savings account. How much money, in dollars, will be in the account at the end of the 4th week of that year?',
        "equations": [],
        "choices": [
            {
                "text": '460'
            },
            {
                "text": '635'
            },
            {
                "text": '639'
            },
            {
                "text": '740'
            }
        ],
        "answer": 3
    },
    "4becad44": {
        "prompt": '3x = 36y - 45\nOne of the two equations in a system of linear equations is given. The system has no solution. Which equation could be the second equation in this system?',
        "equations": [],
        "choices": [
            {
                "text": 'x = 4y'
            },
            {
                "text": '(1/3)x = 4y'
            },
            {
                "text": 'x = 12y - 15'
            },
            {
                "text": '(1/3)x = 12y - 15'
            }
        ],
        "answer": 1
    },
    "520c8177": {
        "prompt": "A veterinarian recommends that each day a certain rabbit should eat 25 calories per pound of the rabbit's weight, plus an additional 11 calories. Which equation represents this situation, where c is the total number of calories the veterinarian recommends the rabbit should eat each day if the rabbit's weight is x pounds?",
        "equations": [],
        "choices": [
            {
                "text": 'c = 25x'
            },
            {
                "text": 'c = 36x'
            },
            {
                "text": 'c = 11x + 25'
            },
            {
                "text": 'c = 25x + 11'
            }
        ],
        "answer": 3
    },
    "88e13c8c": {
        "prompt": 'The total cost f(x), in dollars, to lease a car for 36 months from a particular car dealership is given by f(x) = 36x + 1,000, where x is the monthly payment, in dollars. What is the total cost to lease a car when the monthly payment is $400?',
        "equations": [],
        "choices": [
            {
                "text": '$13,400'
            },
            {
                "text": '$13,000'
            },
            {
                "text": '$15,400'
            },
            {
                "text": '$37,400'
            }
        ],
        "answer": 2
    },
    "3cdbf026": {
        "prompt": 'The graph of the equation ax + ky = 6 is a line in the xy-plane, where a and k are constants. If the line contains the points (-2, -6) and (0, -3), what is the value of k?',
        "equations": [],
        "choices": [
            {
                "text": '-2'
            },
            {
                "text": '-1'
            },
            {
                "text": '2'
            },
            {
                "text": '3'
            }
        ],
        "answer": 0,
        "explanation": 'Choice A is correct. The equation ax + ky = 6 can be rewritten in slope-intercept form. One of the given points, (0, -3), is the y-intercept of the line. Substituting x = 0 and y = -3 into ax + ky = 6 yields k(-3) = 6, so -3k = 6. Dividing both sides by -3 gives k = -2.\n\nChoice B is incorrect and may result from errors made rewriting the given equation.\n\nChoice C is incorrect and may result from errors made rewriting the given equation.\n\nChoice D is incorrect and may result from errors made rewriting the given equation.'
    },
    "8c5e6702": {
        "prompt": 'A window repair specialist charges $220 for the first two hours of repair plus an hourly fee for each additional hour. The total cost for 5 hours of repair is $400. Which function f gives the total cost, in dollars, for x hours of repair, where x ≥ 2?',
        "equations": [],
        "choices": [
            {
                "text": 'f(x) = 60x + 100'
            },
            {
                "text": 'f(x) = 60x + 220'
            },
            {
                "text": 'f(x) = 80x'
            },
            {
                "text": 'f(x) = 80x + 220'
            }
        ],
        "answer": 0
    },
    "3f5a3602": {
        "prompt": 'What system of linear equations is represented by the lines shown?',
        "equations": [],
        "choices": [
            {
                "text": '8x + 4y = 32\n-10x - 4y = -64'
            },
            {
                "text": '8x - 4y = 32\n-10x + 4y = -64'
            },
            {
                "text": '4x - 10y = 32\n-8x + 10y = -64'
            },
            {
                "text": '4x + 10y = 32\n-8x - 10y = -64'
            }
        ],
        "answer": 3,
        "figure": '/qbank/math/figures/3f5a3602.jpg'
    },
    "cfe67646": {
        "prompt": 'The point (8, 2) in the xy-plane is a solution to which of the following systems of inequalities?',
        "equations": [],
        "choices": [
            {
                "text": 'x > 0\ny > 0'
            },
            {
                "text": 'x > 0\ny < 0'
            },
            {
                "text": 'x < 0\ny > 0'
            },
            {
                "text": 'x < 0\ny < 0'
            }
        ],
        "answer": 0
    },
    "84664a7c": {
        "prompt": 'The front of a roller-coaster car is at the bottom of a hill and is 15 feet above the ground. If the front of the roller-coaster car rises at a constant rate of 8 feet per second, which of the following equations gives the height h, in feet, of the front of the roller-coaster car s seconds after it starts up the hill?',
        "equations": [],
        "choices": [
            {
                "text": 'h = 8s + 15'
            },
            {
                "text": 'h = 15s + 1/8'
            },
            {
                "text": 'h = 8s + 1/15'
            },
            {
                "text": 'h = 15s + 8'
            }
        ],
        "answer": 0
    },
    "45cfb9de": {
        "prompt": "Adam's school is a 20-minute walk or a 5-minute bus ride away from his house. The bus runs once every 30 minutes, and the number of minutes, w, that Adam waits for the bus varies between 0 and 30. Which of the following inequalities gives the values of w for which it would be faster for Adam to walk to school?",
        "equations": [],
        "choices": [
            {
                "text": 'w - 5 < 20'
            },
            {
                "text": 'w - 5 > 20'
            },
            {
                "text": 'w + 5 < 20'
            },
            {
                "text": 'w + 5 > 20'
            }
        ],
        "answer": 3
    },
    "979c6ebc": {
        "prompt": '7x + 6y = 5\n28x + 24y = 20\nFor each real number r, which of the following points lies on the graph of each equation in the xy-plane for the given system?',
        "equations": [],
        "choices": [
            {
                "text": '(r, (-6r)/7 + 5/7)'
            },
            {
                "text": '(r, (7r)/6 + 5/6)'
            },
            {
                "text": '(r/4 + 5, -r/4 + 20)'
            },
            {
                "text": '((-6r)/7 + 5/7, r)'
            }
        ],
        "answer": 3
    },
    "c10ad793": {
        "prompt": 'The graph of the linear function f is shown, where y = f(x). What is the x-intercept of the graph of f?',
        "equations": [],
        "choices": [
            {
                "text": '(-12, 0)'
            },
            {
                "text": '(0, 0)'
            },
            {
                "text": '(4, 0)'
            },
            {
                "text": '(12, 0)'
            }
        ],
        "answer": 0,
        "figure": '/qbank/math/figures/c10ad793.jpg'
    },
    "7e3f8363": {
        "prompt": 'In the xy-plane, the graph of the linear function f contains the points (0, 3) and (7, 31). Which equation defines f, where y = f(x)?',
        "equations": [],
        "choices": [
            {
                "text": 'f(x) = 28x + 34'
            },
            {
                "text": 'f(x) = 3x + 38'
            },
            {
                "text": 'f(x) = 4x + 3'
            },
            {
                "text": 'f(x) = 7x + 3'
            }
        ],
        "answer": 2
    },
    "cdec4c87": {
        "prompt": 'y = 12x - 20\ny = 28\nWhat is the solution (x, y) to the given system of equations?',
        "equations": [],
        "choices": [
            {
                "text": '(4, 28)'
            },
            {
                "text": '(20, 28)'
            },
            {
                "text": '(28, 4)'
            },
            {
                "text": '(28, 20)'
            }
        ],
        "answer": 0
    },
    "d11910d6": {
        "prompt": 'The graph of the linear function f is shown. What is the y-intercept of the graph of y = f(x)?',
        "equations": [],
        "choices": [
            {
                "text": '(-5, 0)'
            },
            {
                "text": '(2, 0)'
            },
            {
                "text": '(0, 2)'
            },
            {
                "text": '(0, -5)'
            }
        ],
        "answer": 2,
        "figure": '/qbank/math/figures/d11910d6.jpg'
    },
    "9e5863bd": {
        "prompt": 'For a snowstorm in a certain town, the minimum rate of snowfall recorded was 0.6 inches per hour, and the maximum rate of snowfall recorded was 1.8 inches per hour. Which inequality is true for all values of s, where s represents a rate of snowfall, in inches per hour, recorded for this snowstorm?',
        "equations": [],
        "choices": [
            {
                "text": 's ≥ 2.4'
            },
            {
                "text": 's ≥ 1.8'
            },
            {
                "text": '0 ≤ s ≤ 0.6'
            },
            {
                "text": '0.6 ≤ s ≤ 1.8'
            }
        ],
        "answer": 3
    },
    "842cec4d": {
        "prompt": "During a portion of a flight, a small airplane's cruising speed varied between 150 miles per hour and 170 miles per hour. Which inequality best represents this situation, where s is the cruising speed, in miles per hour, during this portion of the flight?",
        "equations": [],
        "choices": [
            {
                "text": 's ≤ 20'
            },
            {
                "text": 's ≤ 150'
            },
            {
                "text": 's ≤ 170'
            },
            {
                "text": '150 ≤ s ≤ 170'
            }
        ],
        "answer": 3
    },
    "2c121b25": {
        "prompt": 'Valentina bought two containers of beads. In the first container 30% of the beads are red, and in the second container 70% of the beads are red. Together, the containers have at least 400 red beads. Which inequality shows this relationship, where x is the total number of beads in the first container and y is the total number of beads in the second container?',
        "equations": [],
        "choices": [
            {
                "text": '0.3x + 0.7y ≥ 400'
            },
            {
                "text": '0.7x + 0.3y ≤ 400'
            },
            {
                "text": 'x/3 + y/7 ≤ 400'
            },
            {
                "text": '30x + 70y ≥ 400'
            }
        ],
        "answer": 0
    },
    "00ec9102": {
        "prompt": 'Leo goes to a packing store to buy containers and tape. Leo has $15. Each container costs $1.87 and each roll of tape costs $2.40. Which inequality represents the relationship between the number of containers, c, and the number of rolls of tape, t, Leo can buy?',
        "equations": [],
        "choices": [
            {
                "text": '1.87c + 2.40t ≤ 15'
            },
            {
                "text": '1.87c + 2.40t ≥ 15'
            },
            {
                "text": '2.40c + 1.87t ≤ 15'
            },
            {
                "text": '2.40c + 1.87t ≥ 15'
            }
        ],
        "answer": 0
    },
    "4d8ccb96": {
        "prompt": 'A chemist studying the impact of salt on a process mixes x kilograms of a low-salt mixture, which is 2% salt by weight, with y kilograms of a high-salt mixture, which is 96% salt by weight, to create 24 kilograms of a mixture that is 4% salt by weight. Which equation represents this situation?',
        "equations": [],
        "choices": [
            {
                "text": '0.96x + 0.02y = (0.04)(24)'
            },
            {
                "text": '0.02x + 0.96y = (0.04)(24)'
            },
            {
                "text": '0.96x + 0.02y = 24'
            },
            {
                "text": '0.02x + 0.96y = 24'
            }
        ],
        "answer": 1
    },
    "c50ede6d": {
        "prompt": 'The total cost, in dollars, to rent a surfboard consists of a $25 service fee and a $10 per hour rental fee. A person rents a surfboard for t hours and intends to spend a maximum of $75 to rent the surfboard. Which inequality represents this situation?',
        "equations": [],
        "choices": [
            {
                "text": '10t ≤ 75'
            },
            {
                "text": '10 + 25t ≤ 75'
            },
            {
                "text": '25t ≤ 75'
            },
            {
                "text": '25 + 10t ≤ 75'
            }
        ],
        "answer": 3
    },
    "24854644": {
        "prompt": 'What is the equation of the line that passes through the point (0, 5) and is parallel to the graph of y = 7x + 4 in the xy-plane?',
        "equations": [],
        "choices": [
            {
                "text": 'y = 5x'
            },
            {
                "text": 'y = 7x + 5'
            },
            {
                "text": 'y = 7x'
            },
            {
                "text": 'y = 5x + 7'
            }
        ],
        "answer": 1
    },
    "dba8d38a": {
        "prompt": 'A petting zoo sells two types of tickets. The standard ticket, for admission only, costs $5. The premium ticket, which includes admission and food to give to the animals, costs $12. One Saturday, the petting zoo sold a total of 250 tickets and collected a total of $2,300 from ticket sales. Which of the following systems of equations can be used to find the number of standard tickets, s, and premium tickets, p, sold on that Saturday?',
        "equations": [],
        "choices": [
            {
                "text": 's + p = 250\n5s + 12p = 2,300'
            },
            {
                "text": 's + p = 250\n12s + 5p = 2,300'
            },
            {
                "text": '5s + 12p = 250\ns + p = 2,300'
            },
            {
                "text": '12s + 5p = 250\ns + p = 2,300'
            }
        ],
        "answer": 0
    },
    "64c85440": {
        "prompt": "In North America, the standard width of a parking space is at least 7.5 feet and no more than 9.0 feet. A restaurant owner recently resurfaced the restaurant's parking lot and wants to determine the number of parking spaces, n, in the parking lot that could be placed perpendicular to a curb that is 135 feet long, based on the standard width of a parking space. Which of the following describes all the possible values of n?",
        "equations": [],
        "choices": [
            {
                "text": '18 ≤ n ≤ 135'
            },
            {
                "text": '7.5 ≤ n ≤ 9'
            },
            {
                "text": '15 ≤ n ≤ 135'
            },
            {
                "text": '15 ≤ n ≤ 18'
            }
        ],
        "answer": 3
    },
    "7a5a74a6": {
        "prompt": '3(2x - 6) - 11 = 4(x - 3) + 6\nIf x is the solution to the equation above, what is the value of x - 3?',
        "equations": [],
        "choices": [
            {
                "text": '23/2'
            },
            {
                "text": '17/2'
            },
            {
                "text": '15/2'
            },
            {
                "text": '-15/2'
            }
        ],
        "answer": 1,
        "explanation": 'Choice B is correct. Because 2 is a factor of both 2x and 6, the expression 2x - 6 can be rewritten as 2(x - 3). Substituting 2(x - 3) for (2x - 6) on the left-hand side of the given equation yields 3(2)(x - 3) - 11 = 4(x - 3) + 6, or 6(x - 3) - 11 = 4(x - 3) + 6. Subtracting 4(x - 3) from both sides yields 2(x - 3) - 11 = 6. Adding 11 to both sides yields 2(x - 3) = 17. Dividing both sides by 2 yields x - 3 = 17/2.\n\nChoice A is incorrect. This is the value of x, not x - 3.\n\nChoice C is incorrect and may result from calculation errors.\n\nChoice D is incorrect and may result from calculation errors.'
    },
    "e6545fa8": {
        "prompt": 'The graph of a system of linear equations is shown. What is the solution (x, y) to the system?',
        "equations": [],
        "choices": [
            {
                "text": '(2, 3)'
            },
            {
                "text": '(3, 4)'
            },
            {
                "text": '(4, 5)'
            },
            {
                "text": '(5, 6)'
            }
        ],
        "answer": 1,
        "figure": '/qbank/math/figures/e6545fa8.jpg'
    },
    "b7e6394d": {
        "prompt": 'Alan drives an average of 100 miles each week. His car can travel an average of 25 miles per gallon of gasoline. Alan would like to reduce his weekly expenditure on gasoline by $5. Assuming gasoline costs $4 per gallon, which equation can Alan use to determine how many fewer average miles, m, he should drive each week?',
        "equations": [],
        "choices": [
            {
                "text": '(25/4)m = 95'
            },
            {
                "text": '(25/4)m = 5'
            },
            {
                "text": '(4/25)m = 95'
            },
            {
                "text": '(4/25)m = 5'
            }
        ],
        "answer": 3
    },
    "0b221d05": {
        "prompt": 'The shaded region shown represents the solutions to an inequality. Which ordered pair (x, y) is a solution to this inequality?',
        "equations": [],
        "choices": [
            {
                "text": '(-5, -6)'
            },
            {
                "text": '(-2, 5)'
            },
            {
                "text": '(1, 4)'
            },
            {
                "text": '(6, -2)'
            }
        ],
        "answer": 3,
        "figure": '/qbank/math/figures/0b221d05.jpg'
    },
    "968e9e51": {
        "prompt": 'y ≤ x\ny ≤ -x\nWhich of the following ordered pairs (x, y) is a solution to the system of inequalities above?',
        "equations": [],
        "choices": [
            {
                "text": '(1, 0)'
            },
            {
                "text": '(-1, 0)'
            },
            {
                "text": '(0, 1)'
            },
            {
                "text": '(0, -1)'
            }
        ],
        "answer": 3
    },
    "99ea3715": {
        "prompt": 'If the graph of 27x + 33y = 297 is shifted down 5 units in the xy-plane, what is the y-intercept of the resulting graph?',
        "equations": [],
        "choices": [
            {
                "text": '(0, 4)'
            },
            {
                "text": '(0, 6)'
            },
            {
                "text": '(0, 14)'
            },
            {
                "text": '(0, 28)'
            }
        ],
        "answer": 0,
        "explanation": 'Choice A is correct. When the graph of Ax + By = C is shifted down 5 units, the resulting graph can be represented by Ax + B(y + 5) = C. For 27x + 33y = 297 shifted down 5 units, 27x + 33(y + 5) = 297, or 27x + 33y + 165 = 297, so 27x + 33y = 132. The y-intercept occurs when x = 0: 33y = 132, so y = 4. Therefore, the y-intercept is (0, 4).\n\nChoice B is incorrect and may result from conceptual or calculation errors.\n\nChoice C is incorrect and may result from conceptual or calculation errors.\n\nChoice D is incorrect and may result from conceptual or calculation errors.'
    },
    "ee439cff": {
        "prompt": 'On a car trip, Rhett and Jessica each drove for part of the trip, and the total distance they drove was under 220 miles. Rhett drove at an average speed of 35 miles per hour (mph), and Jessica drove at an average speed of 40 mph. Which of the following inequalities represents this situation, where r is the number of hours Rhett drove and j is the number of hours Jessica drove?',
        "equations": [],
        "choices": [
            {
                "text": '35r + 40j > 220'
            },
            {
                "text": '35r + 40j < 220'
            },
            {
                "text": '40r + 35j > 220'
            },
            {
                "text": '40r + 35j < 220'
            }
        ],
        "answer": 1
    },
    "930c2990": {
        "prompt": 'Hydrogen is placed inside a container and kept at a constant pressure. The graph shows the estimated volume y, in liters, of the hydrogen when its temperature is x kelvins. What is the estimated volume, in liters, of the hydrogen when its temperature is 500 kelvins?',
        "equations": [],
        "choices": [
            {
                "text": '0'
            },
            {
                "text": '7/500'
            },
            {
                "text": '7'
            },
            {
                "text": '500/7'
            }
        ],
        "answer": 2,
        "figure": '/qbank/math/figures/930c2990.jpg'
    },
    "317e80f9": {
        "prompt": 'x + y = 18\n5y = x\nWhat is the solution (x, y) to the given system of equations?',
        "equations": [],
        "choices": [
            {
                "text": '(15, 3)'
            },
            {
                "text": '(16, 2)'
            },
            {
                "text": '(17, 1)'
            },
            {
                "text": '(18, 0)'
            }
        ],
        "answer": 0
    },
    "541bef2f": {
        "prompt": 'y ≤ x + 7\ny ≥ -2x - 1\nWhich point (x, y) is a solution to the given system of inequalities in the xy-plane?',
        "equations": [],
        "choices": [
            {
                "text": '(-14, 0)'
            },
            {
                "text": '(0, -14)'
            },
            {
                "text": '(0, 14)'
            },
            {
                "text": '(14, 0)'
            }
        ],
        "answer": 3
    },
    "b2845d88": {
        "prompt": 'Which of the following is an equation of the graph shown in the xy-plane above?',
        "equations": [],
        "choices": [
            {
                "text": 'y = (-1/4)x - 1'
            },
            {
                "text": 'y = -x - 4'
            },
            {
                "text": 'y = -x - 1/4'
            },
            {
                "text": 'y = -4x - 1'
            }
        ],
        "answer": 0,
        "figure": '/qbank/math/figures/b2845d88.jpg'
    },
    "3f5375d9": {
        "prompt": 'The line graphed in the xy-plane below models the total cost, in dollars, for a cab ride, y, in a certain city during nonpeak hours based on the number of miles traveled, x. According to the graph, what is the cost for each additional mile traveled, in dollars, of a cab ride?',
        "equations": [],
        "choices": [
            {
                "text": '$2.00'
            },
            {
                "text": '$2.60'
            },
            {
                "text": '$3.00'
            },
            {
                "text": '$5.00'
            }
        ],
        "answer": 0,
        "figure": '/qbank/math/figures/3f5375d9.jpg'
    },
    "e723bd67": {
        "prompt": '2x - y > 883\nFor which of the following tables are all the values of x and their corresponding values of y solutions to the given inequality?',
        "equations": [],
        "choices": [
            {
                "image": '/qbank/math/choices/e723bd67_0.jpg'
            },
            {
                "image": '/qbank/math/choices/e723bd67_1.jpg'
            },
            {
                "image": '/qbank/math/choices/e723bd67_2.jpg'
            },
            {
                "image": '/qbank/math/choices/e723bd67_3.jpg'
            }
        ],
        "answer": 3
    },
    "a5834ea4": {
        "prompt": 'f(x) = 39\nFor the given linear function f, which table gives three values of x and their corresponding values of f(x)?',
        "equations": [],
        "choices": [
            {
                "image": '/qbank/math/choices/a5834ea4_0.jpg'
            },
            {
                "image": '/qbank/math/choices/a5834ea4_1.jpg'
            },
            {
                "image": '/qbank/math/choices/a5834ea4_2.jpg'
            },
            {
                "image": '/qbank/math/choices/a5834ea4_3.jpg'
            }
        ],
        "answer": 1
    },
    "83f2c3bf": {
        "prompt": 'y = x + 4\nWhich table gives three values of x and their corresponding values of y for the given equation?',
        "equations": [],
        "choices": [
            {
                "image": '/qbank/math/choices/83f2c3bf_0.jpg'
            },
            {
                "image": '/qbank/math/choices/83f2c3bf_1.jpg'
            },
            {
                "image": '/qbank/math/choices/83f2c3bf_2.jpg'
            },
            {
                "image": '/qbank/math/choices/83f2c3bf_3.jpg'
            }
        ],
        "answer": 0
    },
    "a130fcdc": {
        "prompt": 'g(x) = 11x + 4\nFor the given linear function g, which table shows three values of x and their corresponding values of g(x)?',
        "equations": [],
        "choices": [
            {
                "image": '/qbank/math/choices/a130fcdc_0.jpg'
            },
            {
                "image": '/qbank/math/choices/a130fcdc_1.jpg'
            },
            {
                "image": '/qbank/math/choices/a130fcdc_2.jpg'
            },
            {
                "image": '/qbank/math/choices/a130fcdc_3.jpg'
            }
        ],
        "answer": 2
    },
    "d0e614a6": {
        "prompt": '(3/5)x + (3/4)y = 7\nWhich table gives three values of x and their corresponding values of y for the given equation?',
        "equations": [],
        "choices": [
            {
                "image": '/qbank/math/choices/d0e614a6_0.jpg'
            },
            {
                "image": '/qbank/math/choices/d0e614a6_1.jpg'
            },
            {
                "image": '/qbank/math/choices/d0e614a6_2.jpg'
            },
            {
                "image": '/qbank/math/choices/d0e614a6_3.jpg'
            }
        ],
        "answer": 3,
        "explanation": 'Choice D is correct. Each of the tables gives the same three values of x: 1, 2, and 4. Substituting these values into (3/5)x + (3/4)y = 7 shows that the corresponding y-values are 128/15, 116/15, and 92/15, respectively. These pairs match the values in choice D.\n\nChoice A is incorrect because the corresponding y-values do not satisfy the given equation.\n\nChoice B is incorrect because the corresponding y-values do not satisfy the given equation.\n\nChoice C is incorrect because the corresponding y-values do not satisfy the given equation.'
    },
    "3a3b95df": {
        "prompt": 'd = 16 - x/30\nThe equation shown gives the estimated amount of diesel d, in gallons, that remains in the gas tank of a truck after being driven x miles, where 0 ≤ x ≤ 480. What is the estimated amount of diesel, in gallons, that remains in the gas tank of the truck when x = 300?',
        "equations": [],
        "choices": [
            {
                "text": '0'
            },
            {
                "text": '6'
            },
            {
                "text": '14'
            },
            {
                "text": '16'
            }
        ],
        "answer": 1
    },
    "baca4a4c": {
        "prompt": '7(2x - 3) = 63\nWhich equation has the same solution as the given equation?',
        "equations": [],
        "choices": [
            {
                "text": '2x - 3 = 9'
            },
            {
                "text": '2x - 3 = 56'
            },
            {
                "text": '2x - 21 = 63'
            },
            {
                "text": '2x - 21 = 70'
            }
        ],
        "answer": 0
    },
    "be9cb6a2": {
        "prompt": 'The cost of renting a backhoe for up to 10 days is $270 for the first day and $135 for each additional day. Which of the following equations gives the cost y, in dollars, of renting the backhoe for x days, where x is a positive integer and x ≤ 10?',
        "equations": [],
        "choices": [
            {
                "text": 'y = 270x - 135'
            },
            {
                "text": 'y = 270x + 135'
            },
            {
                "text": 'y = 135x + 270'
            },
            {
                "text": 'y = 135x + 135'
            }
        ],
        "answer": 3
    },
    "590f2187": {
        "prompt": 'If 3x - 27 = 24, what is the value of x - 9?',
        "equations": [],
        "choices": [
            {
                "text": '1'
            },
            {
                "text": '8'
            },
            {
                "text": '24'
            },
            {
                "text": '35'
            }
        ],
        "answer": 1
    },
    "f5563c26": {
        "prompt": 'y = 4\nx = y + 6\nThe solution to the given system of equations is (x, y). What is the value of x?',
        "equations": [],
        "choices": [
            {
                "text": '10'
            },
            {
                "text": '6'
            },
            {
                "text": '4'
            },
            {
                "text": '2'
            }
        ],
        "answer": 0
    },
    "38a43902": {
        "prompt": 'y = -2x\n3x + y = 40\nThe solution to the given system of equations is (x, y). What is the value of x?',
        "equations": [],
        "choices": [],
        "answer": '40',
        "acceptedAnswers": [
            '40'
        ]
    },
    "744ee7d7": {
        "prompt": 'The shaded region shown in the graph represents all the solutions to which inequality?',
        "equations": [],
        "choices": [
            {
                "text": 'x ≤ 36'
            },
            {
                "text": 'x ≥ 36'
            },
            {
                "text": 'y ≤ 36'
            },
            {
                "text": 'y ≥ 36'
            }
        ],
        "answer": 3,
        "figure": '/qbank/math/figures/744ee7d7.jpg'
    },
    "05417146": {
        "prompt": 'w + 7 = 357\nWhat value of w is the solution to the given equation?',
        "equations": [],
        "choices": [
            {
                "text": '51'
            },
            {
                "text": '350'
            },
            {
                "text": '364'
            },
            {
                "text": '3,577'
            }
        ],
        "answer": 1
    },
    "6863c7ce": {
        "prompt": 'd = 16t\nThe given equation represents the distance d, in inches, where t represents the number of seconds since an object started moving. Which of the following is the best interpretation of 16 in this context?',
        "equations": [],
        "choices": [
            {
                "text": 'The object moved a total of 16 inches.'
            },
            {
                "text": 'The object moved a total of 16t inches.'
            },
            {
                "text": 'The object is moving at a rate of 16 inches per second.'
            },
            {
                "text": 'The object is moving at a rate of 1/16 inches per second.'
            }
        ],
        "answer": 2
    },
    "51aabd93": {
        "prompt": '(p + 3) + 8 = 10\nWhat value of p is the solution to the given equation?',
        "equations": [],
        "choices": [
            {
                "text": '-1'
            },
            {
                "text": '5'
            },
            {
                "text": '15'
            },
            {
                "text": '21'
            }
        ],
        "answer": 0
    },
    "12ee1edc": {
        "prompt": '(b - 2)x = 8\nIn the given equation, b is a constant. If the equation has no solution, what is the value of b?',
        "equations": [],
        "choices": [
            {
                "text": '2'
            },
            {
                "text": '4'
            },
            {
                "text": '6'
            },
            {
                "text": '10'
            }
        ],
        "answer": 0
    },
    "40ba6288": {
        "prompt": 'If 3x = 30, what is the value of 3x - 12?',
        "equations": [],
        "choices": [
            {
                "text": '-2'
            },
            {
                "text": '18'
            },
            {
                "text": '22'
            },
            {
                "text": '42'
            }
        ],
        "answer": 1
    },
    "ee846db7": {
        "prompt": "A store sells two different-sized containers of a certain Greek yogurt. The store's sales of this Greek yogurt totaled 1,277.94 dollars last month. The equation 5.48x + 7.30y = 1,277.94 represents this situation, where x is the number of smaller containers sold and y is the number of larger containers sold. According to the equation, which of the following represents the price, in dollars, of each smaller container?",
        "equations": [],
        "choices": [
            {
                "text": '5.48'
            },
            {
                "text": '7.30y'
            },
            {
                "text": '7.30'
            },
            {
                "text": '5.48x'
            }
        ],
        "answer": 0
    },
    "f75bd744": {
        "prompt": '4x - 6y = 10y + 2\nty = 1/2 + 2x\nIn the given system of equations, t is a constant. If the system has no solution, what is the value of t?',
        "equations": [],
        "choices": [],
        "answer": '8',
        "acceptedAnswers": [
            '8'
        ]
    },
    "ee2f611f": {
        "prompt": 'A local transit company sells a monthly pass for $95 that allows an unlimited number of trips of any length. Tickets for individual trips cost $1.50, $2.50, or $3.50, depending on the length of the trip. What is the minimum number of trips per month for which a monthly pass could cost less than purchasing individual tickets for trips?',
        "equations": [],
        "choices": [],
        "answer": '28',
        "acceptedAnswers": [
            '28'
        ]
    },
    "fdee0fbf": {
        "prompt": 'In the xy-plane, line k intersects the y-axis at the point (0, -6) and passes through the point (2, 2). If the point (20, w) lies on line k, what is the value of w?',
        "equations": [],
        "choices": [],
        "answer": '74',
        "acceptedAnswers": [
            '74'
        ],
        "explanation": 'The correct answer is 74. Line k intersects the y-axis at (0, -6) and passes through (2, 2). An equation of line k can be written as y = mx - 6. Substituting the point (2, 2) yields 2 = 2m - 6. Adding 6 to both sides yields 8 = 2m, so m = 4. Therefore, y = 4x - 6. Substituting x = 20 yields y = 4(20) - 6 = 74. Since w is the y-coordinate of the point (20, w), w = 74.'
    },
    "ebf8d2b7": {
        "prompt": 'A machine makes large boxes or small boxes, one at a time, for a total of 700 minutes each day. It takes the machine 10 minutes to make a large box or 5 minutes to make a small box. Which equation represents the possible number of large boxes, x, and small boxes, y, the machine can make each day?',
        "equations": [],
        "choices": [
            {
                "text": '5x + 10y = 700'
            },
            {
                "text": '10x + 5y = 700'
            },
            {
                "text": '(x + y)(10 + 5) = 700'
            },
            {
                "text": '(10 + x)(5 + y) = 700'
            }
        ],
        "answer": 1
    },
    "1a1a95de": {
        "prompt": 'A certain open star cluster contains M-type stars and K-type stars. The estimated total mass of M-type and K-type stars in this open star cluster is 127,882 quettagrams. The graph shown models the possible combinations of the number of M-type stars, x, and K-type stars, y, that could be in this open star cluster if all the M-type stars have the same estimated mass and all the K-type stars have the same estimated mass. Based on the graph, which of the following is closest to the estimated mass, in quettagrams, of each M-type star in this cluster?',
        "equations": [],
        "choices": [
            {
                "text": '811'
            },
            {
                "text": '938'
            },
            {
                "text": '51,904'
            },
            {
                "text": '75,978'
            }
        ],
        "answer": 0,
        "figure": '/qbank/math/figures/1a1a95de.jpg'
    },
    "f305b5ca": {
        "prompt": 'Lorenzo purchased a box of cereal and some strawberries at the grocery store. Lorenzo paid $2 for the box of\ncereal and $1.90 per pound for the strawberries. If Lorenzo paid a total of $9.60 for the box of cereal and the\nstrawberries, which of the following equations can be used to find p, the number of pounds of strawberries Lorenzo\npurchased? (Assume there is no sales tax.)',
        "choices": [
            {
                "text": '1.90p + 2 = 9.60'
            },
            {
                "text": '1.90p - 2 = 9.60'
            },
            {
                "text": '1.90 + 2p = 9.60'
            },
            {
                "text": '1.90 - 2p = 9.60'
            }
        ],
        "answer": 0
    },
    "b86123af": {
        "prompt": 'Hiro and Sofia purchased shirts and pants from a store. The price of each shirt purchased was the same and the price of each pair of pants purchased was the same. Hiro purchased 4 shirts and 2 pairs of pants for $86, and Sofia purchased 3 shirts and 5 pairs of pants for $166. Which of the following systems of linear equations represents the situation, if x represents the price, in dollars, of each shirt and y represents the price, in dollars, of each pair of pants?',
        "equations": [],
        "choices": [
            {
                "text": '4x + 2y = 86\n3x + 5y = 166'
            },
            {
                "text": '4x + 3y = 86\n2x + 5y = 166'
            },
            {
                "text": '4x + 2y = 166\n3x + 5y = 86'
            },
            {
                "text": '4x + 3y = 166\n2x + 5y = 86'
            }
        ],
        "answer": 0
    },
    "2937ef4f": {
        "prompt": 'Hector used a tool called an auger to remove corn from a storage bin at a constant rate. The bin contained 24,000 bushels of corn when Hector began to use the auger. After 5 hours of using the auger, 19,350 bushels of corn remained in the bin. If the auger continues to remove corn at this rate, what is the total number of hours Hector will have been using the auger when 12,840 bushels of corn remain in the bin?',
        "equations": [],
        "choices": [
            {
                "text": '3'
            },
            {
                "text": '7'
            },
            {
                "text": '8'
            },
            {
                "text": '12'
            }
        ],
        "answer": 3
    },
    "9b886541": {
        "prompt": 'If 3x - 8 = 7, what is the value of 3x + 8?',
        "equations": [],
        "choices": [
            {
                "text": '-1'
            },
            {
                "text": '5'
            },
            {
                "text": '13'
            },
            {
                "text": '23'
            }
        ],
        "answer": 3
    },
    "0dd6227f": {
        "prompt": 'At how many points do the graphs of the equations y = x + 20 and y = 8x intersect in the xy-plane?',
        "equations": [],
        "choices": [
            {
                "text": '0'
            },
            {
                "text": '1'
            },
            {
                "text": '2'
            },
            {
                "text": '8'
            }
        ],
        "answer": 1
    },
    "0adbe034": {
        "prompt": 'If 4x - 28 = -24, what is the value of x - 7?',
        "equations": [],
        "choices": [
            {
                "text": '-24'
            },
            {
                "text": '-22'
            },
            {
                "text": '-6'
            },
            {
                "text": '-1'
            }
        ],
        "answer": 2
    },
    "1b1deebe": {
        "prompt": 'ax + by = 72\n6x + 2by = 56\nIn the given system of equations, a and b are constants. The graphs of these equations in the xy-plane intersect at the point (4, y). What is the value of a?',
        "equations": [],
        "choices": [
            {
                "text": '3'
            },
            {
                "text": '4'
            },
            {
                "text": '6'
            },
            {
                "text": '14'
            }
        ],
        "answer": 3,
        "explanation": "Choice D is correct. It's given that the graphs of the given system of equations intersect at the point (4, y). Therefore, (4, y) is the solution to the given system. Multiplying the first equation in the given system by -2 yields -2ax - 2by = -144. Adding this equation to the second equation in the system yields (-2a + 6)x + (-2b + 2b)y = -88, or (-2a + 6)x = -88. Since (4, y) is the solution to the system, substituting 4 for x in this equation yields (-2a + 6)(4) = -88. Dividing both sides of this equation by 4 yields -2a + 6 = -22. Subtracting 6 from both sides yields -2a = -28. Dividing both sides by -2 yields a = 14.\n\nChoice A is incorrect and may result from conceptual or calculation errors.\n\nChoice B is incorrect and may result from conceptual or calculation errors.\n\nChoice C is incorrect and may result from conceptual or calculation errors."
    },
    "7efe5495": {
        "prompt": 'y = 3x\n2x + y = 12\nThe solution to the given system of equations is (x, y). What is the value of 5x?',
        "equations": [],
        "choices": [
            {
                "text": '24'
            },
            {
                "text": '15'
            },
            {
                "text": '12'
            },
            {
                "text": '5'
            }
        ],
        "answer": 2
    },
    "27198699": {
        "prompt": 'As part of a science project on evaporation, Amaya measured the height of a liquid in a container over a period of time. The function f(x) = 33 - 0.18x gives the estimated height, in centimeters (cm), of the liquid in the container x days after the start of the project. Which of the following is the best interpretation of 33 in this context?',
        "equations": [],
        "choices": [
            {
                "text": 'The estimated height, in cm, of the liquid at the start of the project'
            },
            {
                "text": 'The estimated height, in cm, of the liquid at the end of the project'
            },
            {
                "text": 'The estimated change in the height, in cm, of the liquid each day'
            },
            {
                "text": 'The estimated number of days for all of the liquid to evaporate'
            }
        ],
        "answer": 0
    },
    "8c98c834": {
        "prompt": 'The equation y = 0.1x models the relationship between the number of different pieces of music a certain pianist practices, y, during an x-minute practice session. How many pieces did the pianist practice if the session lasted 30 minutes?',
        "equations": [],
        "choices": [
            {
                "text": '1'
            },
            {
                "text": '3'
            },
            {
                "text": '10'
            },
            {
                "text": '30'
            }
        ],
        "answer": 1
    },
    "548a4929": {
        "prompt": 'The function h is defined by h(x) = 4x + 28. The graph of y = h(x) in the xy-plane has an x-intercept at (a, 0) and a y-intercept at (0, b), where a and b are constants. What is the value of a + b?',
        "equations": [],
        "choices": [
            {
                "text": '21'
            },
            {
                "text": '28'
            },
            {
                "text": '32'
            },
            {
                "text": '35'
            }
        ],
        "answer": 0
    },
    "bf36c815": {
        "prompt": 'The function g is defined by g(x) = -x + 8. What is the value of g(0)?',
        "equations": [],
        "choices": [
            {
                "text": '-8'
            },
            {
                "text": '0'
            },
            {
                "text": '4'
            },
            {
                "text": '8'
            }
        ],
        "answer": 3
    },
    "9f3cb472": {
        "prompt": 'Line t in the xy-plane has a slope of -1/3 and passes through the point (9, 10). Which equation defines line t?',
        "equations": [],
        "choices": [
            {
                "text": 'y = 13x - 1/3'
            },
            {
                "text": 'y = 9x + 10'
            },
            {
                "text": 'y = -x/3 + 10'
            },
            {
                "text": 'y = -x/3 + 13'
            }
        ],
        "answer": 3
    },
    "d7c8ba0b": {
        "prompt": 'In the xy-plane, line t passes through the points (0, 9) and (1, 17). Which equation defines line t?',
        "equations": [],
        "choices": [
            {
                "text": 'y = (1/8)x + 9'
            },
            {
                "text": 'y = x + 1/8'
            },
            {
                "text": 'y = x + 8'
            },
            {
                "text": 'y = 8x + 9'
            }
        ],
        "answer": 3
    },
    "6fa1dc0f": {
        "prompt": 'Line r in the xy-plane has a slope of 4 and passes through the point (0, 6). Which equation defines line r?',
        "equations": [],
        "choices": [
            {
                "text": 'y = -6x + 4'
            },
            {
                "text": 'y = 6x + 4'
            },
            {
                "text": 'y = 4x - 6'
            },
            {
                "text": 'y = 4x + 6'
            }
        ],
        "answer": 3
    },
    "9d4270fe": {
        "prompt": 'A company that creates and sells tape dispensers calculates its monthly profit, in dollars, by subtracting its fixed monthly costs, in dollars, from its monthly sales revenue, in dollars. The equation 15,000 = 2.00x - 4,500 represents this situation for a month where x tape dispensers are created and sold. Which statement is the best interpretation of 2.00x in this context?',
        "equations": [],
        "choices": [
            {
                "text": 'The monthly sales revenue, in dollars, from selling x tape dispensers'
            },
            {
                "text": 'The monthly sales revenue, in dollars, from each tape dispenser sold'
            },
            {
                "text": 'The monthly cost, in dollars, of creating each tape dispenser'
            },
            {
                "text": 'The monthly cost, in dollars, of creating x tape dispensers'
            }
        ],
        "answer": 0,
        "explanation": "Choice A is correct. It's given that the equation 15,000 = 2.00x - 4,500 represents this situation for a month where x tape dispensers are created and sold. It's also given that the company calculates its monthly profit, in dollars, by subtracting its fixed monthly costs, in dollars, from its monthly sales revenue, in dollars. It follows that 2.00x represents the monthly sales revenue, in dollars. Therefore, the best interpretation of 2.00x in this context is the monthly sales revenue from selling x tape dispensers.\n\nChoice B is incorrect. This is the best interpretation of 2.00, not 2.00x.\n\nChoice C is incorrect and may result from conceptual errors.\n\nChoice D is incorrect. This is the best interpretation of 4,500, not 2.00x."
    },
    "38bf4e04": {
        "prompt": 'A factory makes 9-inch, 7-inch, and 4-inch concrete screws. During a certain day, the number of 9-inch concrete screws that the factory makes is 5 times the number n of 7-inch concrete screws, and the number of 4-inch concrete screws is 22. During this day, the factory makes 100 concrete screws total. Which equation represents this situation?',
        "equations": [],
        "choices": [
            {
                "text": '9(5n)+7n+4(22) = 100'
            },
            {
                "text": '9n+7n+4n = 100'
            },
            {
                "text": '5n+22 = 100'
            },
            {
                "text": '6n+22 = 100'
            }
        ],
        "answer": 3
    },
    "c6b151d4": {
        "prompt": 'A total of 364 paper straws of equal length were used to construct two types of polygons: triangles and rectangles. The triangles and rectangles were constructed so that no two polygons had a common side. The equation 3x + 4y = 364 represents this situation, where x is the number of triangles constructed and y is the number of rectangles constructed. What is the best interpretation of (x, y) = (24, 73) in this context?',
        "equations": [],
        "choices": [
            {
                "text": 'If 24 triangles were constructed, then 73 rectangles were constructed.'
            },
            {
                "text": 'If 24 triangles were constructed, then 73 paper straws were used.'
            },
            {
                "text": 'If 73 triangles were constructed, then 24 rectangles were constructed.'
            },
            {
                "text": 'If 73 triangles were constructed, then 24 paper straws were used.'
            }
        ],
        "answer": 0
    },
    "620fe971": {
        "prompt": 'y = 120 - 25x\nA team of workers has been moving cargo off of a ship. The equation above models the approximate number of tons of cargo, y, that remains to be moved x hours after the team started working. The graph of this equation in the xy-plane is a line. What is the best interpretation of the x-intercept in this context?',
        "equations": [],
        "choices": [
            {
                "text": 'The team will have moved all the cargo in about 4.8 hours.'
            },
            {
                "text": 'The team has been moving about 4.8 tons of cargo per hour.'
            },
            {
                "text": 'The team has been moving about 25 tons of cargo per hour.'
            },
            {
                "text": 'The team started with 120 tons of cargo to move.'
            }
        ],
        "answer": 0
    },
    "9b0a4eae": {
        "prompt": 'The graph in the xy-plane models the possible combinations of length x, in meters (m), and width y, in meters, for a rectangle with a perimeter of 36 m. Which statement is the best interpretation of the point (8, 10) in this context?',
        "equations": [],
        "choices": [
            {
                "text": 'The length is 10 m less than the perimeter, and the width is 8 m less than the perimeter.'
            },
            {
                "text": 'The length is 10 m, and the width is 8 m.'
            },
            {
                "text": 'The length is 8 m, and the width is 10 m.'
            },
            {
                "text": 'The length is 8 m less than the perimeter, and the width is 10 m less than the perimeter.'
            }
        ],
        "answer": 2,
        "figure": '/qbank/math/figures/9b0a4eae.jpg'
    },
    "f14484a5": {
        "prompt": 'A manufacturing plant makes 10-inch, 9-inch, and 7-inch frying pans. During a certain day, the number of 10-inch frying pans that the manufacturing plant makes is 4 times the number n of 9-inch frying pans it makes, and the number of 7-inch frying pans it makes is 10. During this day, the manufacturing plant makes 100 frying pans total. Which equation represents this situation?',
        "equations": [],
        "choices": [
            {
                "text": '10(4n) + 9n + 7(10) = 100'
            },
            {
                "text": '10n + 9n + 7n = 100'
            },
            {
                "text": '4n + 10 = 100'
            },
            {
                "text": '5n + 10 = 100'
            }
        ],
        "answer": 3
    },
    "797a81fb": {
        "prompt": '-12x + 14y = 36\n-6x + 7y = -18\nHow many solutions does the given system of equations have?',
        "equations": [],
        "choices": [
            {
                "text": 'Exactly one'
            },
            {
                "text": 'Exactly two'
            },
            {
                "text": 'Infinitely many'
            },
            {
                "text": 'Zero'
            }
        ],
        "answer": 3,
        "explanation": 'Choice D is correct. The second equation, -6x + 7y = -18, has coefficients of x and y that are half those in the first equation, -12x + 14y = 36. However, the constant terms are not proportional in the same way, since 36/2 = 18 but the second equation has constant term -18. Therefore, the lines are parallel and distinct, so the system has zero solutions.\n\nChoice A is incorrect. The system does not have exactly one solution because the lines do not intersect.\n\nChoice B is incorrect. A system of two linear equations cannot have exactly two solutions.\n\nChoice C is incorrect. The system does not have infinitely many solutions because the equations are not equivalent.'
    },
    "2b15d65f": {
        "explanation": "Choice A is correct. Let the economist's model be the linear function Q = mP + b, where Q is the demand, P is the selling price, m is the slope of the line, and b is the y-coordinate of the y-intercept of the line in the xy-plane. Two points that satisfy the function are (40, 20,000) and (60, 15,000). The slope m can be found using m = (15,000 - 20,000)/(60 - 40) = -5,000/20 = -250. Therefore, Q = -250P + b. Substituting the point (40, 20,000) yields 20,000 = -250(40) + b, or 20,000 = -10,000 + b. Adding 10,000 to both sides yields b = 30,000. Therefore, the model is Q = -250P + 30,000. Substituting 55 for P yields Q = -250(55) + 30,000 = 16,250. It follows that when the selling price is $55 per unit, the demand is 16,250 units.\n\nChoice B is incorrect and may result from calculation or conceptual errors.\n\nChoice C is incorrect and may result from calculation or conceptual errors.\n\nChoice D is incorrect and may result from calculation or conceptual errors.",
        "prompt": 'An economist modeled the demand Q for a certain product as a linear function of the selling price P. The demand\nwas 20,000 units when the selling price was $40 per unit, and the demand was 15,000 units when the selling price\nwas $60 per unit. Based on the model, what is the demand, in units, when the selling price is $55 per unit?',
        "choices": [
            {
                "text": '16,250'
            },
            {
                "text": '16,500'
            },
            {
                "text": '16,750'
            },
            {
                "text": '17,500'
            }
        ],
        "answer": 0
    },
    "b23bba4c": {
        "explanation": "Choice B is correct. It's given that a represents the number of small boxes and b represents the number of large boxes the customer had shipped. If the customer had 3 small boxes shipped, then a = 3. Substituting 3 for a in the equation 3a + 4b = 25 yields 3(3) + 4b = 25, or 9 + 4b = 25. Subtracting 9 from both sides yields 4b = 16. Dividing both sides by 4 yields b = 4. Therefore, the customer had 4 large boxes shipped.\n\nChoice A is incorrect. If b = 3, then 3a + 4(3) = 25, so 3a + 12 = 25 and a = 13/3, which is not 3.\n\nChoice C is incorrect. If b = 5, then 3a + 4(5) = 25, so 3a + 20 = 25 and a = 5/3, which is not 3.\n\nChoice D is incorrect. If b = 6, then 3a + 4(6) = 25, so 3a + 24 = 25 and a = 1/3, which is not 3.",
        "prompt": '3a + 4b = 25\nA shipping company charged a customer $25 to ship some small boxes and some large boxes. The equation above represents the relationship between a, the number of small boxes, and b, the number of large boxes, the customer had shipped. If the customer had 3 small boxes shipped, how many large boxes were shipped?',
        "equations": [],
        "choices": [
            {
                "text": '3'
            },
            {
                "text": '4'
            },
            {
                "text": '5'
            },
            {
                "text": '6'
            }
        ],
        "answer": 1
    },
    "f224df07": {
        "explanation": 'Choice C is correct. Let a equal the number of 120-pound packages and b equal the number of 100-pound packages. The conditions are a + b ≥ 10 and 120a + 100b ≤ 1,100. To maximize a, take the minimum number of packages, a + b = 10, so b = 10 - a. Substituting into the weight inequality yields 120a + 100(10 - a) ≤ 1,100, or 20a + 1,000 ≤ 1,100, so 20a ≤ 100 and a ≤ 5. When a = 5 and b = 5, the total weight is 1,100 pounds, which is allowed. Therefore, the maximum number of 120-pound packages is 5.\n\nChoice A is incorrect and may result from conceptual or calculation errors.\n\nChoice B is incorrect and may result from conceptual or calculation errors.\n\nChoice D is incorrect. If a = 6, then even with b = 4 the weight is 120(6) + 100(4) = 1,120, which exceeds 1,100 pounds.'
    },
    "608eeb6e": {
        "explanation": 'Choice C is correct. From the first equation, 5x = 15, so x = 3. Substituting x = 3 into the second equation -4x + y = -2 yields -4(3) + y = -2, or -12 + y = -2. Adding 12 to both sides yields y = 10. Therefore, x + y = 3 + 10 = 13.\n\nChoice A is incorrect and may result from conceptual or calculation errors.\n\nChoice B is incorrect. This is the value of -(x + y).\n\nChoice D is incorrect and may result from conceptual or calculation errors.'
    },
    "06fc1726": {
        "explanation": 'Choice C is correct. If f(x) = (2x - 1)/3, then f(5) = (2(5) - 1)/3 = (10 - 1)/3 = 9/3 = 3.\n\nChoice A is incorrect and may result from not multiplying x by 2 in the numerator.\n\nChoice B is incorrect and may result from dividing 2x by 3 and then subtracting 1.\n\nChoice D is incorrect and may result from evaluating only the numerator 2x - 1.'
    },
}


def repair(byid: dict[str, dict], bank: fitz.Document) -> list[str]:
    touched: list[str] = []

    for qid, patch in TEXT_FIXES.items():
        if qid not in byid:
            continue
        byid[qid].update(patch)
        touched.append(qid)

    # Tables (images OK)
    for i, rows in enumerate(
        [
            [["0", "0"], ["1", "0"], ["2", "0"]],
            [["0", "39"], ["1", "39"], ["2", "39"]],
            [["0", "0"], ["1", "39"], ["2", "78"]],
            [["0", "39"], ["1", "0"], ["2", "-39"]],
        ]
    ):
        render_table(["x", "f(x)"], rows, MATH_CHOICE_IMG / f"a5834ea4_{i}.jpg")
    byid["a5834ea4"]["choices"] = [
        {"image": f"/qbank/math/choices/a5834ea4_{i}.jpg"} for i in range(4)
    ]
    touched.append("a5834ea4")

    for i, rows in enumerate(
        [
            [["-1", "7"], ["0", "11"], ["1", "15"]],
            [["-1", "-4"], ["0", "0"], ["1", "4"]],
            [["-1", "-7"], ["0", "4"], ["1", "15"]],
            [["-1", "-11"], ["0", "0"], ["1", "11"]],
        ]
    ):
        render_table(["x", "g(x)"], rows, MATH_CHOICE_IMG / f"a130fcdc_{i}.jpg")
    byid["a130fcdc"]["choices"] = [
        {"image": f"/qbank/math/choices/a130fcdc_{i}.jpg"} for i in range(4)
    ]
    touched.append("a130fcdc")

    for i, rows in enumerate(
        [
            [["440", "0"], ["441", "-2"], ["442", "-4"]],
            [["440", "0"], ["442", "-2"], ["441", "-4"]],
            [["442", "0"], ["440", "-2"], ["441", "-4"]],
            [["442", "0"], ["441", "-2"], ["440", "-4"]],
        ]
    ):
        render_table(["x", "y"], rows, MATH_CHOICE_IMG / f"e723bd67_{i}.jpg")
    byid["e723bd67"]["choices"] = [
        {"image": f"/qbank/math/choices/e723bd67_{i}.jpg"} for i in range(4)
    ]
    touched.append("e723bd67")

    for i, rows in enumerate(
        [
            [["0", "4"], ["1", "5"], ["2", "6"]],
            [["0", "6"], ["1", "5"], ["2", "4"]],
            [["0", "2"], ["1", "1"], ["2", "0"]],
            [["0", "0"], ["1", "1"], ["2", "2"]],
        ]
    ):
        render_table(["x", "y"], rows, MATH_CHOICE_IMG / f"83f2c3bf_{i}.jpg")
    byid["83f2c3bf"]["choices"] = [
        {"image": f"/qbank/math/choices/83f2c3bf_{i}.jpg"} for i in range(4)
    ]
    touched.append("83f2c3bf")

    for i, rows in enumerate(
        [
            [["1", "113/20"], ["2", "101/20"], ["4", "77/20"]],
            [["1", "47/5"], ["2", "44/5"], ["4", "38/5"]],
            [["1", "148/15"], ["2", "136/15"], ["4", "112/15"]],
            [["1", "128/15"], ["2", "116/15"], ["4", "92/15"]],
        ]
    ):
        render_table(["x", "y"], rows, MATH_CHOICE_IMG / f"d0e614a6_{i}.jpg")
    byid["d0e614a6"]["choices"] = [
        {"image": f"/qbank/math/choices/d0e614a6_{i}.jpg"} for i in range(4)
    ]
    touched.append("d0e614a6")

    # Figures / graphs only (text choices elsewhere)
    page = page_for(bank, "744ee7d7")
    fig, _ = crop_math_figure(page, MATH_FIG / "744ee7d7.jpg", page.get_text())
    byid["744ee7d7"].update(
        prompt="The shaded region shown in the graph represents all the solutions to which inequality?",
        equations=[],
        figure=(f"/{fig}" if fig and not str(fig).startswith("/") else fig),
        choices=[
            {"text": "x <= 36"},
            {"text": "x >= 36"},
            {"text": "y <= 36"},
            {"text": "y >= 36"},
        ],
        answer=3,
    )
    touched.append("744ee7d7")

    # Recrop known figures if bank available
    fig_clips = {
        "b0fc3166": (28, 150, 380, 430),
        "b2845d88": (16, 138, 140, 216),
        "3f5a3602": (28, 155, 375, 430),
        "c10ad793": (40, 155, 300, 445),
        "d11910d6": (40, 155, 300, 445),
        "e6545fa8": (28, 155, 380, 430),
        "0b221d05": (40, 155, 340, 445),
        "930c2990": (30, 150, 400, 500),
    }
    for qid, clip in fig_clips.items():
        if qid not in byid:
            continue
        page = page_for(bank, qid)
        rel = render_clip(page, MATH_FIG / f"{qid}.jpg", fitz.Rect(*clip), scale=3.2)
        byid[qid]["figure"] = f"/{rel}" if not str(rel).startswith("/") else rel
        touched.append(qid)

    # cab graph: embedded image bbox
    page = page_for(bank, "3f5375d9")
    for info in page.get_image_info(xrefs=True):
        if info.get("width", 0) > 100:
            rel = render_clip(
                page, MATH_FIG / "3f5375d9.jpg", fitz.Rect(info["bbox"]), scale=3.5
            )
            byid["3f5375d9"]["figure"] = f"/{rel}" if not str(rel).startswith("/") else rel
            touched.append("3f5375d9")
            break

    if byid.get("1a1a95de", {}).get("prompt", "").startswith("on the graph"):
        byid["1a1a95de"]["prompt"] = "Based " + byid["1a1a95de"]["prompt"]
        touched.append("1a1a95de")

    # Hard rule: Educator Algebra never keeps equation image slots.
    for qid, q in byid.items():
        if q.get("pool") != "E. Bank" or q.get("domain") != "Algebra":
            continue
        if q.get("equations"):
            q["equations"] = []
            touched.append(qid)

    return touched


def main() -> None:
    if not BANK_PDF.exists():
        raise SystemExit(f"Missing bank PDF: {BANK_PDF}")
    qs = json.loads(DATA.read_text(encoding="utf-8"))
    byid = {q["id"]: q for q in qs}
    bank = fitz.open(BANK_PDF)
    touched = repair(byid, bank)
    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Repaired {len(set(touched))} questions: {', '.join(sorted(set(touched)))}")


if __name__ == "__main__":
    main()
