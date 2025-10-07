# app.py
# -------------------------------
# Punto de entrada principal
# Ejecuta todo el flujo y genera el mapa final

from map_interactive import preparar_datos, calcular_indice_accesibilidad, generar_mapa

if __name__ == "__main__":
    gimnasios, buffer_500, buffer_1000, barrios = preparar_datos()
    barrios = calcular_indice_accesibilidad(barrios, buffer_500)
    generar_mapa(gimnasios, buffer_500, buffer_1000, barrios)
