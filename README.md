# 📦 Buscador de Ofertas Laborales LATAM (Streamlit + Docker)

Esta aplicación permite realizar búsquedas de ofertas laborales en los principales portales de empleo de América Latina utilizando scraping con Python. La interfaz está construida en Streamlit, y el sistema está contenerizado con Docker y orquestado con Redis para caching temporal.

## 🌐 Portales soportados
- LinkedIn *(requiere navegador Playwright)*
- Computrabajo *(HTML estático)*
- Bumeran *(requiere navegador Playwright)*
- Indeed *(HTML estático)*
- Jooble *(HTML estático)*
- Glassdoor *(requiere navegador Playwright)*

## 🧰 Tecnologías
- Python 3.10
- Streamlit
- Requests + BeautifulSoup4
- Playwright (Chromium headless)
- Redis (para cachear resultados)
- Docker & Docker Compose

---

## 🚀 Instrucciones de uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/job-search-streamlit.git
cd job-search-streamlit
```

### 2. Construir e iniciar los contenedores
```bash
docker-compose up --build
```

### 3. Acceder a la app
Abre tu navegador en [http://localhost:8501](http://localhost:8501)

---

## 🖥️ Interfaz de usuario

Desde la interfaz Streamlit puedes:
- Ingresar **palabras clave** (ej: `python`, `data scientist`, etc.)
- Especificar **país o región**
- Seleccionar uno o más portales
- Elegir cuántas páginas de resultados scrapea por portal
- Incluir o excluir portales que requieren JavaScript (uso de navegador)

Los resultados se muestran en una tabla y pueden descargarse como archivo CSV.

---

## ⚙️ Arquitectura interna

- Cada scraper se encuentra en el módulo `scrapers/` y hereda de `JobScraper`
- Control de **cuota de requests** (10 por minuto por portal)
- Soporte para **rotación de proxies** (puedes configurar tu lista en la clase base)
- Uso de **Redis como caché en memoria**, purgado al reiniciar
- **Playwright** se usa solo cuando es necesario (portales dinámicos)

---

## 🧩 Agregar nuevos portales
1. Crear un nuevo archivo en `scrapers/` (ej: `trabajando_scraper.py`)
2. Crear una clase que herede de `JobScraper` e implemente el método `scrape()`
3. Registrar el nuevo scraper en `streamlit_app.py`

---

## 📌 Notas
- El uso de proxies es opcional, pero recomendado para evitar bloqueos
- Este proyecto es solo para fines educativos e investigación. Respeta los términos de servicio de cada portal
- LinkedIn y Glassdoor pueden aplicar restricciones adicionales

---

## 📬 Contacto
Desarrollado por: **Matilde I Césari**  
Repositorio: [github.com/matucesari/job-search-streamlit](https://github.com/matucesari/job-search-streamlit)

## ✅ Fix

1. Error en Indeed y Jooble: problema de dominio punycode "México"
Causa: El país "México" fue interpretado como parte del subdominio y convertido automáticamente a punycode (xn--mxico-bsa).
Solución: En el scraper de Indeed y Jooble, debemos usar el código de país estándar (por ejemplo, mx) como parte del dominio, no el nombre completo.

Modificar en los scrapers:
<
base_url = f"https://{country.lower()}.indeed.com/jobs"
>
por:

<
country_code = {"argentina": "ar", "mexico": "mx", "chile": "cl", "colombia": "co", ...}
base_url = f"https://{country_code.get(country.lower(), 'www')}.indeed.com/jobs"
>
Y lo mismo para Jooble.

También podríamos aplicar una función de normalización de país que remapee "México" → "mx", "Argentina" → "ar", etc.

 2. Error en Bumeran:
Causa: Estás haciendo: for card in soup.select(".aviso a.aviso_link"),:
    card.select_one(...)
pero soup.select(...) ya devuelve una lista, y al agregar , estás creando una tupla de una lista, no iterando sobre los elementos. Es un error sutil de sintaxis.
Reemplazá:
<
for card in soup.select(".aviso a.aviso_link"),:
>
por:
<
for card in soup.select(".aviso a.aviso_link"):
>

## ✅ Recomendaciones:
Agregar try/except por scraper para capturar excepciones y continuar con los demás portales sin frenar la app.
* Mostrar logs de errores al usuario (como estás haciendo).
* Probar con otros términos (python, data, analista) para descartar que no haya resultados reales.
* Hacer debug con st.write(soup.prettify()[:1000]) para ver si se está obteniendo el HTML esperado.


