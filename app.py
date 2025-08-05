import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st

from eduparser.pipeline import EduParserConfig, run_pipeline
from eduparser.pdf_extractor import extract_text
from eduparser.content_cleaner import clean_text
from eduparser.faiss_indexer import DEFAULT_MODEL


st.set_page_config(page_title="EduParser")
st.title("EduParser GUI")

uploaded = st.file_uploader(
    "Belge yükle", type=["pdf", "docx", "txt", "html", "htm"]
)
grade = st.selectbox("Sınıf", [str(i) for i in range(1, 9)])
course = st.text_input("Ders adı")
topic = st.text_input("Konu adı")
max_tokens = st.slider("Token sayısı", 50, 1000, 300, step=50)

use_uuid = st.checkbox("UUID tabanlı ID kullan")

build_index = st.checkbox("FAISS index oluşturulsun mu?")
model_name: Optional[str] = None
if build_index:
    model_name = st.text_input("Model adı", value=DEFAULT_MODEL)

convert = st.button("Dönüştür")


@st.cache_data(show_spinner=False)
def cached_clean_text(file_bytes: bytes, filename: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = Path(tmp.name)
    try:
        text = extract_text(tmp_path)
        return clean_text(text)
    finally:
        tmp_path.unlink(missing_ok=True)


if convert:
    if not uploaded or not course or not topic:
        st.error("Lütfen dosya seçip tüm alanları doldurun.")
    else:
        progress = st.progress(0)
        status = st.empty()

        def update(step: int, total: int) -> None:
            progress.progress(step / total)

        cleaned = cached_clean_text(uploaded.getvalue(), uploaded.name)

        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "output.jsonl"
            index_path = Path(tmpdir) / "output.faiss" if build_index else None

            metadata = {"sınıf": grade, "ders": course, "konu": topic}
            config = EduParserConfig(
                source_path=uploaded.name,
                out_path=jsonl_path,
                metadata=metadata,
                max_tokens=max_tokens,
                id_strategy="uuid" if use_uuid else "simple",
                index_path=index_path,
                model_name=model_name or DEFAULT_MODEL,
            )

            records = run_pipeline(
                config, text=cleaned, progress_cb=update
            )

            progress.empty()
            status.text("İşlem tamamlandı.")

            st.success(f"{len(records)} kayıt üretildi.")

            avg_tokens = sum(len(r["content"].split()) for r in records) / len(records)
            st.write(
                f"Toplam chunk sayısı: {len(records)}, Ortalama uzunluk: {avg_tokens:.1f} kelime"
            )

            st.subheader("Önizleme")
            st.table(records[:3])

            json_bytes = jsonl_path.read_bytes()

            with st.expander("İndirme Linkleri"):
                st.download_button("JSONL indir", json_bytes, "output.jsonl", "application/json")

                if build_index and index_path and index_path.exists():
                    faiss_bytes = index_path.read_bytes()
                    st.download_button(
                        "FAISS indir", faiss_bytes, "output.faiss", "application/octet-stream",
                    )
                    ids_bytes = (index_path.with_suffix(index_path.suffix + ".ids")).read_bytes()
                    st.download_button(
                        "ID dosyasını indir",
                        ids_bytes,
                        "output.faiss.ids",
                        "application/json",
                    )
