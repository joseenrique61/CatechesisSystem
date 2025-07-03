# app/main/services/pdf_service.py

from fpdf import FPDF
from datetime import datetime
from app.main.helpers import *

class PDFService:
    def generate_catechizing_certificate(self, catechizing_data, parish_data):
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", size=12)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Certificado de Catequesis", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        
        full_name = "Nombre no disponible"
        if catechizing_data.Person:
            full_name = f"{catechizing_data.Person.FirstName or ''} {catechizing_data.Person.FirstSurname or ''}".strip()

        level_name = "Nivel no asignado"
        if catechizing_data.Class and catechizing_data.Class.Level:
            level_name = catechizing_data.Class.Level.Name

        parish_name = "Parroquia no asignada"
        if (parish_data):
            parish_name = parish_data.Name
        
        texto_certificado = (
            f"Por la presente se certifica que\n\n"
            f"{full_name}\n\n"
            f"ha completado satisfactoriamente el nivel de catequesis de\n\n"
            f"'{level_name}'\n\n"
            f"en la Parroquia {parish_name}.\n\n"
            f"Emitido el {datetime.now().strftime('%d de %B de %Y')}."
        )
        
        pdf.multi_cell(0, 10, txt=texto_certificado, align='C')

        pdf.ln(20)
        pdf.cell(0, 10, txt="________________________", ln=True, align='C')
        pdf.cell(0, 10, txt="Párroco", ln=True, align='C')

        pdf_byte_array = pdf.output() # fpdf2 es mejor que el antiguo dest='S'...
        return bytes(pdf_byte_array)

    def generate_parish_report(self, catechizings_data, sacrament_filter=None):
        """
        Genera un reporte de los catequizandos de la parroquia de forma robusta y mantenible.
        Recibe una lista de CatechizingDTOs.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # --- 1. Título del Reporte ---
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Reporte de Catequizandos", ln=True, align='C')
        if sacrament_filter:
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, txt=f"(Filtrado por: {sacrament_filter})", ln=True, align='C')
        pdf.ln(10)

        # --- 2. Definición y Dibujo de la Tabla ---
        # Constantes para fácil mantenimiento
        HEADERS = ['Nombre Completo', 'Edad', 'Nivel Actual']
        COL_WIDTHS = [80, 20, 80] # Anchos de las columnas (total 180mm)

        self._draw_header(pdf, HEADERS, COL_WIDTHS)
        
        pdf.set_font("Arial", '', 10)
        if not catechizings_data:
            pdf.cell(0, 10, "No hay datos para mostrar en este reporte.", border=1, ln=True, align='C')
        else:
            for catechizing in catechizings_data:
                self._draw_row(pdf, catechizing, COL_WIDTHS)

        # --- 3. Salida del PDF ---
        # Se mantiene la conversión explícita a bytes para máxima compatibilidad
        return bytes(pdf.output())

    # --- Métodos privados de ayuda ---
    
    def _draw_header(self, pdf, headers, col_widths):
        """Dibuja la cabecera de la tabla."""
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(230, 230, 230) # Un gris claro para el fondo del header
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', fill=True)
        pdf.ln()

    def _draw_row(self, pdf, catechizing, col_widths):
        """Dibuja una fila de datos en la tabla, manejando datos faltantes."""
        # Preparación de datos con valores por defecto para evitar errores
        full_name = "Sin nombre"
        if catechizing.Person:
            first_name = catechizing.Person.FirstName or ""
            first_surname = catechizing.Person.FirstSurname or ""
            full_name = f"{first_name} {first_surname}".strip()

        age = "N/A"
        if catechizing.Person and catechizing.Person.BirthDate:
            age_num = calculate_age(catechizing.Person.BirthDate)
            age = str(age_num) if age_num is not None else "N/A"

        level_name = "Sin nivel asignado"
        if catechizing.Class and catechizing.Class.Level and catechizing.Class.Level.Name:
            level_name = catechizing.Class.Level.Name
            
        # Truncamos texto para que no se desborde (ajusta los números según necesites)
        # Esto es más simple que usar multi_cell para filas complejas.
        full_name = (full_name[:45] + '...') if len(full_name) > 48 else full_name
        level_name = (level_name[:45] + '...') if len(level_name) > 48 else level_name

        row_data = [full_name, age, level_name]

        # Dibujar celdas
        for i, data in enumerate(row_data):
            align = 'C' if i == 1 else 'L' # Centrar la edad, alinear el resto a la izquierda
            pdf.cell(col_widths[i], 10, txt=str(data), border=1, align=align)
        pdf.ln()
