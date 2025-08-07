import argparse
import itertools
import logging
import math
import typing
from pdb import set_trace

import numpy as np
import sympy
from sympy import symbols
from sympy.ntheory.factor_ import totient
from tqdm import tqdm


def sym_inverse_eye(n):
    A = sympy.zeros(n)
    for ii in range(n):
        A[ii, n - ii - 1] = 1
    return A


def line_group_sympy_withparities(DictParams, symprec=1e-6):
    family = DictParams["family"]
    if family == 6:
        qpoint = DictParams["qpoints"]
        nrot = DictParams["nrot"]
        a = DictParams["a"]
        order = DictParams["order"]
        k1, m1, n, piV = symbols("k1 m1 n piV")

        func0 = sympy.Matrix(
            [
                1,
                sympy.exp(1j * k1 * a),
                sympy.exp(1j * m1 * 2 * sympy.pi / n),
                piV,
            ]
        )
        func1 = [
            sympy.Matrix([[1, 0], [0, 1]]),
            sympy.Matrix(
                [
                    [
                        sympy.exp(1j * k1 * a),
                        0,
                    ],
                    [
                        0,
                        sympy.exp(1j * k1 * a),
                    ],
                ]
            ),
            sympy.Matrix(
                [
                    [
                        sympy.exp(1j * m1 * 2 * sympy.pi / n),
                        0,
                    ],
                    [
                        0,
                        sympy.exp(-1j * m1 * 2 * sympy.pi / n),
                    ],
                ]
            ),
            sympy.Matrix([[0, 1], [1, 0]]),
        ]
        func = [func0, func1]
        qps_value = [qpoint]
        m1_value = list(range(0, int(nrot / 2) + 1))
        # set_trace()

        def value_fc(fc, tmp_k1, tmp_m1, tmp_piV, nrot, order):
            res = []
            for tmp_order in order:
                for jj, tmp in enumerate(tmp_order):
                    if jj == 0:
                        tmp0 = fc[tmp]
                    else:
                        tmp0 = fc[tmp] * tmp0
                tmp1 = tmp0.evalf(
                    subs={k1: tmp_k1, m1: tmp_m1, n: nrot, piV: tmp_piV}
                )
                res.append(tmp1)
            return res

        paras_km = list(itertools.product(*[qps_value, m1_value]))
        paras_symbol = [k1, m1, piV]
        characters, paras_values = [], []
        for ii, paras_value in enumerate(paras_km):
            tmp_k1, tmp_m1 = paras_value
            if np.isclose(tmp_m1, 0, atol=symprec) or np.isclose(
                tmp_m1, nrot / 2, atol=symprec
            ):
                idx_fc = 0
                fc = func[idx_fc]
                for tmp_piV in [-1, 1]:
                    res = value_fc(fc, tmp_k1, tmp_m1, tmp_piV, nrot, order)
                    characters.append(np.array(res).astype(np.complex128))
                    paras_values.append([tmp_k1, tmp_m1, tmp_piV])
            else:
                idx_fc = 1
                fc = func[idx_fc]
                tmp_piV = 0
                res = value_fc(fc, tmp_k1, tmp_m1, tmp_piV, nrot, order)
                characters.append(np.array(res).astype(np.complex128))
                paras_values.append([tmp_k1, tmp_m1, tmp_piV])

    elif family == 8:
        qpoint = DictParams["qpoints"]
        nrot = DictParams["nrot"]
        a = DictParams["a"]
        order = DictParams["order"]

        k1, m1, n, piV = symbols("k1 m1 n piV")
        func0 = sympy.Matrix(
            [
                1,
                sympy.exp(1j * (k1 * a / 2 + m1 * sympy.pi / n)),
                1,
                piV,
            ]
        )

        func1 = [
            sympy.Matrix([[1, 0], [0, 1]]),
            sympy.Matrix(
                [
                    [
                        sympy.exp(1j * (k1 * a / 2 + m1 * sympy.pi / n)),
                        0,
                    ],
                    [
                        0,
                        sympy.exp(1j * (k1 * a / 2 - m1 * sympy.pi / n)),
                    ],
                ]
            ),
            sympy.Matrix(
                [
                    [
                        sympy.exp(1j * m1 * 2 * sympy.pi / n),
                        0,
                    ],
                    [
                        0,
                        sympy.exp(-1j * m1 * 2 * sympy.pi / n),
                    ],
                ]
            ),
            sympy.Matrix([[0, 1], [1, 0]]),
        ]

        func = [func0, func1]
        qps_value = [qpoint]
        m1_value = list(range(0, nrot + 1))

        def value_fc(fc, tmp_k1, tmp_m1, tmp_piV, nrot, order):
            res = []
            for tmp_order in order:
                for jj, tmp in enumerate(tmp_order):
                    if jj == 0:
                        tmp0 = fc[tmp]
                    else:
                        tmp0 = fc[tmp] * tmp0
                tmp1 = tmp0.evalf(
                    subs={k1: tmp_k1, m1: tmp_m1, n: nrot, piV: tmp_piV}
                )
                res.append(tmp1)
            return res

        paras_km = list(itertools.product(*[qps_value, m1_value]))
        paras_symbol = [k1, m1, piV]
        characters, paras_values = [], []
        for ii, paras_value in enumerate(paras_km):
            tmp_k1, tmp_m1 = paras_value
            if np.isclose(tmp_m1, 0, atol=symprec) or np.isclose(
                tmp_m1, nrot, atol=symprec
            ):
                idx_fc = 0
                fc = func[idx_fc]
                for tmp_piV in [-1, 1]:
                    res = value_fc(fc, tmp_k1, tmp_m1, tmp_piV, nrot, order)
                    characters.append(np.array(res).astype(np.complex128))
                    paras_values.append([tmp_k1, tmp_m1, tmp_piV])
            else:
                idx_fc = 1
                fc = func[idx_fc]
                tmp_piV = 0
                res = value_fc(fc, tmp_k1, tmp_m1, tmp_piV, nrot, order)
                characters.append(np.array(res).astype(np.complex128))
                paras_values.append([tmp_k1, tmp_m1, tmp_piV])
    elif family == 13:
        qpoint = DictParams["qpoints"]
        nrot = DictParams["nrot"]
        a = DictParams["a"]
        order = DictParams["order"]
        n, k1, m1, f, piU, piV, piH = symbols("n k1 m1 f piU piV piH")

        func0 = sympy.Matrix(
            [
                1,
                sympy.exp(1j * m1 * sympy.pi / n),
                1,
                piU,
                piV,
            ]
        )
        func1 = [
            sympy.Matrix(
                [
                    [1, 0],
                    [0, 1],
                ]
            ),
            sympy.Matrix(
                [
                    [sympy.exp(1j * m1 * sympy.pi / n), 0],
                    [0, sympy.exp(-1j * m1 * sympy.pi / n)],
                ]
            ),
            sympy.Matrix(
                [
                    [
                        sympy.exp(1j * 2 * m1 * sympy.pi / n),
                        0,
                    ],
                    [
                        0,
                        sympy.exp(-1j * 2 * m1 * sympy.pi / n),
                    ],
                ]
            ),
            sympy.Matrix(
                [
                    [
                        0,
                        piH,
                    ],
                    [
                        piH,
                        0,
                    ],
                ]
            ),
            sympy.Matrix([[0, 1], [1, 0]]),
        ]
        func2 = [
            sympy.Matrix([[1, 0], [0, 1]]),
            sympy.Matrix(
                [
                    [sympy.exp(1j * (m1 * sympy.pi / n + k1 * a / 2)), 0],
                    [0, sympy.exp(1j * (m1 * sympy.pi / n - k1 * a / 2))],
                ]
            ),
            # sympy.Matrix([[0, 1], [1, 0]]),
            sympy.Matrix([[1, 0], [0, 1]]),
            sympy.Matrix([[0, piV], [piV, 0]]),
            sympy.Matrix([[piV, 0], [0, piV]]),
        ]
        func3 = [
            sympy.Matrix([[1, 0], [0, 1]]),
            sympy.Matrix([[-1, 0], [0, 1]]),
            sympy.Matrix([[-1, 0], [0, -1]]),
            sympy.Matrix([[piU, 0], [0, piU]]),
            sympy.Matrix([[0, 1], [1, 0]]),
        ]
        func4 = [
            sympy.Matrix(
                [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            ),
            sympy.Matrix(
                [
                    [
                        sympy.exp(1j * (m1 * sympy.pi / n + k1 * a / 2)),
                        0,
                        0,
                        0,
                    ],
                    [
                        0,
                        sympy.exp(1j * (-m1 * sympy.pi / n + k1 * a / 2)),
                        0,
                        0,
                    ],
                    [
                        0,
                        0,
                        sympy.exp(1j * (m1 * sympy.pi / n - k1 * a / 2)),
                        0,
                    ],
                    [
                        0,
                        0,
                        0,
                        sympy.exp(-1j * (m1 * sympy.pi / n + k1 * a / 2)),
                    ],
                ]
            ),
            sympy.Matrix(
                [
                    [sympy.exp(1j * 2 * sympy.pi * m1 / n), 0, 0, 0],
                    [0, sympy.exp(-1j * 2 * sympy.pi * m1 / n), 0, 0],
                    [0, 0, sympy.exp(1j * 2 * sympy.pi * m1 / n), 0],
                    [0, 0, 0, sympy.exp(-1j * 2 * sympy.pi * m1 / n)],
                ]
            ),
            sympy.Matrix(
                [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]
            ),
            sympy.Matrix(
                [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
            ),
        ]

        func = [func0, func1, func2, func3, func4]
        qps_value = [qpoint]

        if np.isclose(np.abs(qpoint), np.pi / a, atol=symprec):
            m1_value = list(range(0, np.floor(nrot / 2 + 1).astype(np.int32)))
            # m1_value = list(range(-np.floor(nrot / 2 + 1).astype(np.int32) + 1, np.floor(nrot / 2 + 1).astype(np.int32)))
        else:
            m1_value = list(range(0, nrot + 1))
            # m1_value = list(range(-nrot + 1, nrot + 1))

        def value_fc(
            fc,
            tmp_k1,
            tmp_m1,
            tmp_piU,
            tmp_piV,
            tmp_piH,
            nrot,
            a,
            order,
        ):
            res = []
            for tmp_order in order:
                for jj, tmp in enumerate(tmp_order):
                    if jj == 0:
                        tmp0 = fc[tmp]
                    else:
                        # tmp0 = fc[tmp] * tmp0
                        tmp0 = tmp0 * fc[tmp]
                tmp1 = tmp0.xreplace(
                    {
                        k1: tmp_k1,
                        m1: tmp_m1,
                        n: nrot,
                        f: a / 2,
                        piU: tmp_piU,
                        piV: tmp_piV,
                        piH: tmp_piH,
                    }
                )
                res.append(tmp1)
            return res

        paras_km = list(itertools.product(*[qps_value, m1_value]))
        paras_symbol = [k1, m1, piU, piV, piH]
        characters, paras_values = [], []
        for ii, paras_value in enumerate(paras_km):
            tmp_k1, tmp_m1 = paras_value
            if np.isclose(tmp_k1, 0, atol=symprec):
                if np.isclose(np.abs(tmp_m1), 0) or np.isclose(
                    np.abs(tmp_m1), nrot
                ):
                    idx_fc = 0
                    fc = func[idx_fc]
                    tmp_piH = 0
                    for tmp_piU, tmp_piV in itertools.product(
                        [-1, 1], [-1, 1]
                    ):
                        res = value_fc(
                            fc,
                            tmp_k1,
                            tmp_m1,
                            tmp_piU,
                            tmp_piV,
                            tmp_piH,
                            nrot,
                            a,
                            order,
                        )
                        characters.append(np.array(res).astype(np.complex128))
                        # paras_values.append([tmp_k1, tmp_m1, tmp_piU, tmp_piV])
                        # paras_symbol.append([k1, m1, piU, piV])
                        paras_values.append(
                            [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                        )
                else:
                    idx_fc = 1
                    fc = func[idx_fc]
                    tmp_piU, tmp_piV = 0, 0
                    for tmp_piH in [-1, 1]:
                        res = value_fc(
                            fc,
                            tmp_k1,
                            tmp_m1,
                            tmp_piU,
                            tmp_piV,
                            tmp_piH,
                            nrot,
                            a,
                            order,
                        )
                        characters.append(np.array(res).astype(np.complex128))
                        # paras_values.append([tmp_k1, tmp_m1, tmp_piH])
                        paras_values.append(
                            [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                        )
                        # paras_symbol.append([k1, m1, piH])

            elif np.isclose(np.abs(tmp_k1), np.pi / a, atol=symprec):
                if np.isclose(np.abs(tmp_m1), nrot / 2, atol=symprec):
                    idx_fc = 3
                    fc = func[idx_fc]
                    tmp_piV, tmp_piH = 0, 0
                    for tmp_piU in [-1, 1]:
                        res = value_fc(
                            fc,
                            tmp_k1,
                            tmp_m1,
                            tmp_piU,
                            tmp_piV,
                            tmp_piH,
                            nrot,
                            a,
                            order,
                        )
                        characters.append(np.array(res).astype(np.complex128))
                        # paras_values.append([tmp_k1, tmp_m1, tmp_piU])
                        # paras_symbol.append([k1, m1, piU])
                        paras_values.append(
                            [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                        )

                elif np.isclose(np.abs(tmp_m1), 0, atol=symprec):
                    idx_fc = 2
                    fc = func[idx_fc]
                    tmp_piU, tmp_piH = 0, 0
                    for tmp_piV in [-1, 1]:
                        res = value_fc(
                            fc,
                            tmp_k1,
                            tmp_m1,
                            tmp_piU,
                            tmp_piV,
                            tmp_piH,
                            nrot,
                            a,
                            order,
                        )
                        characters.append(np.array(res).astype(np.complex128))
                        # paras_values.append([tmp_k1, tmp_m1, tmp_piV])
                        # paras_symbol.append([k1, m1, piV])
                        paras_values.append(
                            [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                        )

                else:
                    idx_fc = 4
                    fc = func[idx_fc]
                    tmp_piU, tmp_piV, tmp_piH = 0, 0, 0
                    res = value_fc(
                        fc,
                        tmp_k1,
                        tmp_m1,
                        tmp_piU,
                        tmp_piV,
                        tmp_piH,
                        nrot,
                        a,
                        order,
                    )
                    characters.append(np.array(res).astype(np.complex128))
                    # paras_values.append([tmp_k1, tmp_m1])
                    # paras_symbol.append([k1, m1])
                    paras_values.append(
                        [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                    )

            elif 0 < np.abs(tmp_k1) < np.pi / a:
                if np.isclose(np.abs(tmp_m1), 0, atol=symprec) or np.isclose(
                    np.abs(tmp_m1), nrot, atol=symprec
                ):
                    idx_fc = 2
                    fc = func[idx_fc]
                    tmp_piU, tmp_piH = 0, 0
                    for tmp_piV in [-1, 1]:
                        res = value_fc(
                            fc,
                            tmp_k1,
                            tmp_m1,
                            tmp_piU,
                            tmp_piV,
                            tmp_piH,
                            nrot,
                            a,
                            order,
                        )
                        characters.append(np.array(res).astype(np.complex128))
                        # paras_values.append([tmp_k1, tmp_m1, tmp_piV])
                        # paras_symbol.append([k1, m1, piV])
                        paras_values.append(
                            [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                        )

                else:
                    idx_fc = 4
                    fc = func[idx_fc]
                    tmp_piU, tmp_piV, tmp_piH = 0, 0, 0
                    res = value_fc(
                        fc,
                        tmp_k1,
                        tmp_m1,
                        tmp_piU,
                        tmp_piV,
                        tmp_piH,
                        nrot,
                        a,
                        order,
                    )
                    characters.append(np.array(res).astype(np.complex128))
                    # paras_values.append([tmp_k1, tmp_m1])
                    # paras_symbol.append([k1, m1])
                    paras_values.append(
                        [tmp_k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH]
                    )

            else:
                set_trace()
                logging.ERROR("Wrong value for k1")

    else:
        raise NotImplementedError("Family %d is not supported yet" % family)
    return characters, paras_values, paras_symbol
