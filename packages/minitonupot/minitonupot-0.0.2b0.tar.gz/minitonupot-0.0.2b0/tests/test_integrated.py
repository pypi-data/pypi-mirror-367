import unittest
from booster import (
    generar_estructura,
    aumentar_capacidad,
    normalizar_datos,
    crear_entorno_virtual,
    instalar_dependencias,
    limpiar_cache,
    eliminar_restos,
    generar_configuracion,
    inicializar_proyecto
)

class TestIntegratedSystem(unittest.TestCase):

    # 1–10: Validaciones de parámetros
    def test_generar_estructura_tipo(self):
        self.assertIsInstance(generar_estructura(), dict)

    def test_aumentar_capacidad_tipo(self):
        resultado = aumentar_capacidad({'nivel': 1})
        self.assertIn('nivel', resultado)

    def test_normalizar_datos_formato(self):
        datos = {'A': 10, 'B': 20}
        normalizados = normalizar_datos(datos)
        self.assertIsInstance(normalizados, dict)

    def test_normalizar_datos_llaves(self):
        datos = {'A': 10, 'B': 20}
        normalizados = normalizar_datos(datos)
        self.assertSetEqual(set(normalizados.keys()), set(datos.keys()))

    def test_crear_entorno_virtual_ok(self):
        self.assertTrue(crear_entorno_virtual(nombre="testenv"))

    def test_instalar_dependencias_lista(self):
        resultado = instalar_dependencias(['numpy', 'pandas'])
        self.assertIn('numpy', resultado)

    def test_instalar_dependencias_vacia(self):
        self.assertEqual(instalar_dependencias([]), [])

    def test_limpiar_cache_devuelve_bool(self):
        self.assertIn(limpiar_cache(), [True, False])

    def test_eliminar_restos_tipo(self):
        self.assertIsInstance(eliminar_restos(), str)

    def test_generar_configuracion_formato(self):
        conf = generar_configuracion()
        self.assertIn('nombre', conf)

    # 11–30: Ejecución correcta
    def test_inicializar_proyecto_dict(self):
        res = inicializar_proyecto("test123")
        self.assertIsInstance(res, dict)

    def test_inicializar_proyecto_nombre(self):
        res = inicializar_proyecto("miniproyecto")
        self.assertIn('nombre', res)

    def test_crear_entorno_multiple(self):
        for i in range(3):
            self.assertTrue(crear_entorno_virtual(f'env_{i}'))

    def test_instalar_dependencias_basicas(self):
        basicos = ['requests', 'flask']
        salida = instalar_dependencias(basicos)
        for dep in basicos:
            self.assertIn(dep, salida)

    def test_repetida_generacion_estructura(self):
        estructuras = [generar_estructura() for _ in range(3)]
        for estructura in estructuras:
            self.assertIn('estructura', estructura)

    def test_cache_limpiar_repetido(self):
        for _ in range(3):
            self.assertIn(limpiar_cache(), [True, False])

    def test_inicializar_proyecto_nombre_tipo(self):
        resultado = inicializar_proyecto("proyecto_prueba")
        self.assertEqual(resultado['nombre'], "proyecto_prueba")

    def test_normalizar_datos_requiere_dict(self):
        with self.assertRaises(TypeError):
            normalizar_datos(["A", "B"])

    def test_generar_configuracion_contiene_clave(self):
        config = generar_configuracion()
        self.assertTrue('version' in config)

    def test_eliminar_restos_formato(self):
        resultado = eliminar_restos()
        self.assertTrue("archivos" in resultado or "limpiado" in resultado)

    # 31–45: Errores controlados
    def test_instalar_dependencia_inexistente(self):
        salida = instalar_dependencias(['nonexistentpackage999'])
        self.assertIn('nonexistentpackage999', salida)

    def test_entorno_nombre_vacio(self):
        with self.assertRaises(ValueError):
            crear_entorno_virtual(nombre="")

    def test_aumentar_capacidad_sin_argumento(self):
        with self.assertRaises(TypeError):
            aumentar_capacidad()

    def test_normalizar_datos_nulo(self):
        with self.assertRaises(TypeError):
            normalizar_datos(None)

    def test_inicializar_proyecto_vacio(self):
        with self.assertRaises(ValueError):
            inicializar_proyecto("")

    def test_generar_estructura_existe_clave(self):
        self.assertTrue('estructura' in generar_estructura())

    def test_configuracion_version_formato(self):
        self.assertRegex(generar_configuracion().get('version', ''), r'^\d+\.\d+')

    def test_limpiar_cache_retorna_estado(self):
        estado = limpiar_cache()
        self.assertIsInstance(estado, bool)

    def test_eliminar_restos_no_nulo(self):
        self.assertIsNotNone(eliminar_restos())

    def test_generar_configuracion_devuelve_dict(self):
        self.assertIsInstance(generar_configuracion(), dict)

    # 46–65: Integraciones cruzadas
    def test_boost_configuracion_aumentada(self):
        config = generar_configuracion()
        resultado = aumentar_capacidad(config)
        self.assertIn('nivel', resultado)

    def test_ciclo_basico_proyecto(self):
        nombre = "project_test"
        crear_entorno_virtual(nombre)
        config = generar_configuracion()
        self.assertTrue(isinstance(config, dict))

    def test_entorno_limpieza_loop(self):
        for _ in range(5):
            limpiar_cache()
            eliminar_restos()
        self.assertTrue(True)

    def test_normalizacion_e_integridad(self):
        datos = {'X': 5, 'Y': 10}
        n = normalizar_datos(datos)
        self.assertTrue(all(0 <= val <= 1 for val in n.values()))

    def test_generar_y_usar_config(self):
        config = generar_configuracion()
        resultado = aumentar_capacidad(config)
        self.assertTrue('nivel' in resultado)

    def test_instalacion_y_limpieza(self):
        instalar_dependencias(['pytest'])
        self.assertIn(limpiar_cache(), [True, False])

    def test_proyecto_entero(self):
        nombre = "superproyecto"
        inicializar_proyecto(nombre)
        config = generar_configuracion()
        aumentar_capacidad(config)
        limpiar_cache()
        self.assertTrue(True)

    def test_entorno_virtual_multiple(self):
        nombres = ['env1', 'env2', 'env3']
        for nombre in nombres:
            self.assertTrue(crear_entorno_virtual(nombre))

    def test_aumento_con_normalizacion(self):
        data = {'a': 100, 'b': 50}
        normalizados = normalizar_datos(data)
        resultado = aumentar_capacidad(normalizados)
        self.assertTrue('nivel' in resultado)

    def test_combinacion_general(self):
        entorno = crear_entorno_virtual("mega")
        config = generar_configuracion()
        deps = instalar_dependencias(['flask'])
        self.assertTrue(entorno and isinstance(config, dict) and 'flask' in deps)

    # 66–75: Tipos de retorno y consistencia
    def test_tipos_generados(self):
        self.assertIsInstance(generar_estructura(), dict)
        self.assertIsInstance(generar_configuracion(), dict)

    def test_todo_retornos_validos(self):
        self.assertIn(limpiar_cache(), [True, False])
        self.assertIsInstance(eliminar_restos(), str)

    def test_normalizacion_rango(self):
        datos = {'x': 50, 'y': 100}
        n = normalizar_datos(datos)
        for val in n.values():
            self.assertLessEqual(val, 1)

    def test_config_version_existe(self):
        self.assertIn('version', generar_configuracion())

    def test_instalar_dependencias_vacia_comprueba(self):
        deps = instalar_dependencias([])
        self.assertEqual(deps, [])

    # 76–80: Robustez múltiple
    def test_loop_generacion(self):
        for _ in range(10):
            estructura = generar_estructura()
            self.assertIn('estructura', estructura)

    def test_loop_instalacion_falsa(self):
        for _ in range(3):
            resultado = instalar_dependencias(['fakepkg123'])
            self.assertIn('fakepkg123', resultado)

    def test_entorno_loop_validos(self):
        for i in range(3):
            self.assertTrue(crear_entorno_virtual(f"test_env_{i}"))

    def test_instalacion_repetida(self):
        paquetes = ['rich']
        for _ in range(2):
            self.assertIn('rich', instalar_dependencias(paquetes))

    def test_completo_y_ok(self):
        nombre = "prueba_final"
        inicializar_proyecto(nombre)
        config = generar_configuracion()
        resultado = aumentar_capacidad(config)
        self.assertIn('nivel', resultado)

if __name__ == '__main__':
    unittest.main()
