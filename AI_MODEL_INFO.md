# AI Model Information

## Użyty Model: BLIP (Bootstrapping Language-Image Pre-training)

### Szczegóły Modelu

**Nazwa:** `Salesforce/blip-image-captioning-base`

**Typ:** Vision-Language Model (VLM) - Image Captioning

**Architektura:**
- Transformer-based model
- Pre-trained on large-scale image-text pairs
- Fine-tuned for image captioning task

### Charakterystyka

**Rozmiar modelu:** ~990 MB (po pobraniu)
- To jest "base" wersja - najmniejsza wersja BLIP
- Lżejsza niż większe modele (np. BLIP-large)

**Parametry:** ~247M parametrów (szacunkowo dla base version)

**Zastosowanie:**
- Generowanie opisów obrazów (image captioning)
- Działa lokalnie (bez potrzeby zewnętrznych API)
- Wspiera język angielski

**Wymagania:**
- PyTorch
- Transformers library
- Działa na CPU (może być wolne) lub GPU (szybsze)

### Dlaczego "Tiny AI"?

Model jest nazywany "tiny" w kontekście:
- **Rozmiar:** ~990MB to relatywnie mało w porównaniu do większych modeli (np. GPT-3: 175GB)
- **Wydajność:** Działa na CPU, nie wymaga potężnego GPU
- **Lokalny:** Wszystko działa na twoim komputerze, bez wysyłania danych na zewnątrz

### Alternatywne modele (jeśli chcesz zmienić)

Możesz zmienić model w `backend/services/ai_model_integration.py`:

```python
# Obecny (base - najmniejszy)
self.model_name = "Salesforce/blip-image-captioning-base"

# Większe wersje (lepsza jakość, ale większy rozmiar):
# self.model_name = "Salesforce/blip-image-captioning-large"  # ~1.4GB
```

### Wydajność

- **CPU:** ~5-15 sekund na obraz (zależnie od CPU)
- **GPU:** ~1-3 sekundy na obraz (jeśli masz CUDA)

### Jakość

Model generuje krótkie, zwięzłe opisy obrazów w języku angielskim.
Przykłady z twojej bazy:
- "a cat standing on top of a wooden shelf"
- "the theatre logo"
- "a cat laying on the floor next to a plant"

