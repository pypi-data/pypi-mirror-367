import unittest

# Simulamos que estas funciones existen en tu paquete real
# Si tienes funciones específicas en minitonupot, puedes importarlas directamente:
# from minitonupot import alguna_funcion

def suma(a, b):
    return a + b

def resta(a, b):
    return a - b

def multiplica(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("División por cero no permitida")
    return a / b

def es_par(n):
    return n % 2 == 0

class TestMinipotBasics(unittest.TestCase):

    def test_suma(self):
        self.assertEqual(suma(3, 2), 5)

    def test_resta(self):
        self.assertEqual(resta(10, 4), 6)

    def test_multiplicacion(self):
        self.assertEqual(multiplica(6, 7), 42)

    def test_division(self):
        self.assertAlmostEqual(divide(10, 2), 5.0)

    def test_es_par(self):
        self.assertTrue(es_par(8))
        self.assertFalse(es_par(7))

    def test_division_por_cero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)
