# streamlit_app.py

import streamlit as st
import pandas as pd
import importlib
import os

# Diccionario de scrapers disponibles
SCRAPER_CLASSES = {
    "LinkedIn": "linkedin_scraper.LinkedInScraper",
    "Computrabajo": "computrabajo_scraper.ComputrabajoScraper",
    "Bumeran": "bumeran_scraper.BumeranScraper",
    "Indeed": "indeed_scraper.IndeedScraper",
    "Jooble": "jooble_scraper.JoobleScraper",
    "Glassdoor": "glassdoor_scraper.GlassdoorScraper",
}

# Configuración de página
st.set_page_config(page_title="Buscador de Empleos LATAM", layout="wide")
st.title("🔍 Buscador de Ofertas Laborales en América Latina")

# Formulario de parámetros de búsqueda
with st.form("search_form"):
    keywords = st.text_input("Palabras clave", "python data scientist")
    country = st.text_input("País o región (en inglés o ISO-2)", "Argentina")
    selected_sites = st.multiselect(
        "Selecciona portales a consultar",
        options=list(SCRAPER_CLASSES.keys()),
        default=["LinkedIn", "Computrabajo", "Indeed"]
    )
    pages = st.slider("Cantidad de páginas por portal", 1, 5, 1)
    use_browser = st.checkbox("Usar navegador (JS) para sitios dinámicos", value=True)
    submit = st.form_submit_button("Buscar")

if submit:
    st.info("⏳ Iniciando búsqueda, esto puede demorar unos segundos...")
    all_results = []
    progress = st.progress(0)
    step = 1 / len(selected_sites)

    for i, site in enumerate(selected_sites):
        module_name, class_name = SCRAPER_CLASSES[site].split(".")
        module = importlib.import_module(f"scrapers.{module_name}")
        ScraperClass = getattr(module, class_name)

        # Omitir sitios con JS si se desactiva el navegador
        if not use_browser and site in ["LinkedIn", "Glassdoor", "Bumeran"]:
            continue

        scraper = ScraperClass()
        try:
            jobs = scraper.scrape(keywords, country, pages)
            all_results.extend(jobs)
        except Exception as e:
            st.warning(f"⚠️ Error en {site}: {e}")
        progress.progress((i + 1) * step)

    if all_results:
        df = pd.DataFrame(all_results)
        st.success(f"✅ Se encontraron {len(df)} ofertas laborales.")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, "ofertas.csv", "text/csv")
    else:
        st.error("❌ No se encontraron resultados para los parámetros indicados.")

