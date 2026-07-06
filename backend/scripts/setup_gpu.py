#!/usr/bin/env python3
"""
FinSense AI — GPU Setup Verification Script

Run this script to verify your CUDA environment:
    python scripts/setup_gpu.py

Output includes:
- CUDA availability
- GPU device info
- FAISS GPU support
- PyTorch version
- Recommended settings
"""

import sys
import platform


def check_python():
    print(f"🐍 Python {sys.version}")
    if sys.version_info < (3, 11):
        print("⚠️  Python 3.11+ recommended")


def check_cuda():
    print("\n── CUDA / PyTorch ────────────────────────────────────────")
    try:
        import torch

        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            print(f"   CUDA version:   {torch.version.cuda}")
            count = torch.cuda.device_count()
            print(f"   GPU count:      {count}")
            for i in range(count):
                props = torch.cuda.get_device_properties(i)
                vram_gb = props.total_memory / (1024 ** 3)
                print(f"   GPU {i}: {props.name}")
                print(f"          VRAM:    {vram_gb:.1f} GB")
                print(f"          Compute: {props.major}.{props.minor}")
                print(f"          Tensor cores: {'Yes' if props.major >= 7 else 'No'}")

            # Test basic CUDA operation
            x = torch.randn(1000, 1000).cuda()
            y = x @ x.T
            print("✅ CUDA tensor operations: OK")

            # Mixed precision test
            if torch.cuda.get_device_properties(0).major >= 7:
                with torch.autocast("cuda"):
                    z = x @ x.T
                print("✅ Mixed precision (FP16): OK")
        else:
            print("ℹ️  Running in CPU-only mode (CUDA not available)")
            print("   To enable GPU: install CUDA 12 + torch with cu121")

    except ImportError:
        print("❌ PyTorch not installed")
        print("   CPU install: pip install torch")
        print("   GPU install: pip install torch --index-url https://download.pytorch.org/whl/cu121")


def check_faiss():
    print("\n── FAISS ─────────────────────────────────────────────────")
    try:
        import faiss

        print(f"✅ FAISS {faiss.__version__ if hasattr(faiss, '__version__') else 'installed'}")

        if hasattr(faiss, "StandardGpuResources"):
            res = faiss.StandardGpuResources()
            d = 128
            index_cpu = faiss.IndexFlatL2(d)
            index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)
            print("✅ FAISS-GPU: Available and working")
        else:
            print("ℹ️  FAISS-CPU installed (no GPU acceleration for vector search)")
            print("   GPU upgrade: pip uninstall faiss-cpu && pip install faiss-gpu")
    except ImportError:
        print("❌ FAISS not installed: pip install faiss-cpu")
    except Exception as e:
        print(f"⚠️  FAISS-GPU test failed: {e} — falling back to CPU")


def check_google_ai():
    print("\n── Google Generative AI ─────────────────────────────────")
    try:
        import google.generativeai as genai
        print(f"✅ google-generativeai installed")
    except ImportError:
        print("❌ Not installed: pip install google-generativeai")


def check_langchain():
    print("\n── LangChain / LangGraph ────────────────────────────────")
    try:
        import langchain
        print(f"✅ LangChain {langchain.__version__}")
    except ImportError:
        print("❌ LangChain not installed")

    try:
        import langgraph
        print(f"✅ LangGraph {langgraph.__version__}")
    except ImportError:
        print("❌ LangGraph not installed")


def check_sentence_transformers():
    print("\n── Sentence Transformers (optional GPU embeddings) ──────")
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        if torch.cuda.is_available():
            model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
            test_emb = model.encode(["test sentence"])
            print(f"✅ sentence-transformers (GPU): OK — embedding dim {len(test_emb[0])}")
        else:
            print("ℹ️  sentence-transformers installed (GPU not available)")
    except ImportError:
        print("ℹ️  sentence-transformers not installed (optional)")


def print_recommendations():
    print("\n── Recommendations ──────────────────────────────────────")
    try:
        import torch
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            vram = props.total_memory / (1024 ** 3)
            if vram >= 16:
                batch_size = 256
                tier = "High-end"
            elif vram >= 8:
                batch_size = 128
                tier = "Mid-range"
            elif vram >= 4:
                batch_size = 64
                tier = "Entry-level"
            else:
                batch_size = 32
                tier = "Limited"

            print(f"GPU Tier:            {tier} ({vram:.1f} GB)")
            print(f"Recommended batch:   EMBEDDING_BATCH_SIZE={batch_size}")
            print(f"Mixed precision:     MIXED_PRECISION={'true' if props.major >= 7 else 'false'}")
            print(f"FAISS GPU:           FAISS_USE_GPU=true")
        else:
            print("Running on CPU — all features work but GPU acceleration unavailable")
            print("Set ENABLE_GPU=false in your .env file")
    except ImportError:
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("  FinSense AI — GPU Environment Verification")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")

    check_python()
    check_cuda()
    check_faiss()
    check_google_ai()
    check_langchain()
    check_sentence_transformers()
    print_recommendations()

    print("\n" + "=" * 60)
    print("Setup complete! Start the server with:")
    print("  uvicorn app.main:app --reload --port 8000")
    print("=" * 60)
