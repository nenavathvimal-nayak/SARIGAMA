# Third-Party Notices & Open-Source Compliance

This document details the third-party components, upstream foundations, and open-source licenses incorporated into or utilized by **SARIGAMA**.

---

## 1. Upstream Foundation

### ACE-Step 1.5
- **Project**: ACE-Step 1.5 Music Generation Engine
- **Upstream Repository**: [https://github.com/ace-step/ACE-Step-1.5](https://github.com/ace-step/ACE-Step-1.5)
- **Paper**: *ACE-Step 1.5: Pushing the Boundaries of Open-Source Music Generation* (arXiv:2602.00744)
- **Authors**: Junmin Gong, Yulin Song, Wenxiao Zhao, Sen Wang, Shengyuan Xu, Jing Guo
- **License**: MIT License
- **Copyright**: Copyright (c) 2026 ACEStep

```text
MIT License

Copyright (c) 2026 ACEStep

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 2. Vendored Third-Party Code

### nano-vllm
- **Location**: `acestep/third_parts/nano-vllm`
- **Origin**: [https://github.com/Xingkai-Yu/nano-vllm](https://github.com/Xingkai-Yu/nano-vllm)
- **License**: MIT License
- **Copyright**: Copyright (c) 2025 Xingkai Yu

```text
MIT License

Copyright (c) 2025 Xingkai Yu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 3. Pre-Trained Model Weights & Terms of Use

SARIGAMA downloads and uses pre-trained weights for inference and generation:

| Component | Model Name | Source / Provider | License / Conditions |
|-----------|------------|-------------------|----------------------|
| DiT Generator | `acestep-v15-*` (turbo, sft, base, xl) | ACE-Step / Hugging Face | Upstream ACE-Step Model Terms |
| LM Planner | `acestep-5Hz-lm-*` (0.6B, 1.7B, 4B) | ACE-Step / Qwen Team | Apache 2.0 (Qwen Base) + ACE-Step Terms |
| Audio Codec | VAE / SoundStream / EnCodec | Upstream Research | Open-Source Research Use |

*Note: Model weights are not stored in this Git repository; they are downloaded dynamically from authenticated model repositories upon first run.*
