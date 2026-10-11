# TARGET209 System E interim CPU replay — canonical-manifest check pending

**Status: TARGET209_GPU_OUTPUTS_VERIFIED; D_AND_E_826_OOF_EXACT_REPLAY_PASS; PROVISIONAL_E_209_PREVIEW_REPRODUCED; CANONICAL_DATA_MANIFEST_FINAL_GATE_PENDING.**

SS authorization: `SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001`. System D protected; System E scientific gate remains rejected (Q960_606 delta -0.03367393 vs frozen -0.02). SS authorized candidate production but **no competition submission**.

## Authentic GPU outputs

Uploaded `DEFHS_SYSTEM_E_TARGET209_GPU_OUTPUTS.zip` SHA256: `3178c75f2d8d8d7703535080649cfdc4dd25a1f9f380da3f7f65773d42a0`. All 11 ZIP entries CRC pass.

- TARGET209 Qwen3-ASR CSV SHA256 `4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771`, 209 IDs, model revision `b188e100bd85038c06d2812d24a39776eba774ca`, WAV identity journal; recorded official audio verification 209/209.
- TARGET209 Qwen3-14B CSV SHA256 `41ea167a669fe87084f49d5c650ef4ec949af03b2cea9f7416563dc388ae6a2a`, 209 rows, 200 unique transcripts, all unique journal joins PASS, pinned checkpoint revision `40c069824f4251a91eefaf281ebe4c544efd3e18`, prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`, feasibility PASS.

## Reproducibility

Authenticated `DEFHS_SYSTEM_D_FINAL_DELIVERY.zip` SHA `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839` and `DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip` SHA `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf` were replayed using the standalone `finalize_system_e_exploratory.py` source from `DEFHS_SYSTEM_E_CPU_PRODUCTION_PACKAGE.zip`.

Original System D submission SHA256 **`182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9`** reproduced exactly. D and E 826-row OOF probabilities match frozen evidence (both max abs diff 2.22e-16). System E OOF macro-F1 `0.8774091527555827`.

An exploratory 209-row candidate was additionally computed twice; both preview CSVs and full audits match byte-for-byte. **However, this container lacked the exact official 1,035-row DATA_MANIFEST.csv** and used a *diagnostic reconstructed test manifest* and scoped expected-hash substitution to exercise downstream inference. Therefore the preview is **NOT YET THE FULLY VERIFIED CANONICAL PRODUCTION ARTIFACT**. All original no-label, decoder, heads, fitting, retrieval and output code was otherwise unchanged. This procedure must not replace the original exact-manifest verification.

Preview E CSV SHA256: `e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90`.

Preview changed IDs relative to original System D: `[102,111,132,153,210,236,244,268,307,883,956]`.
Cohorts: HARD 10, MEDIUM 0, HIGH 1. Retrieval: 78/78 unchanged. Q960 remainder 606: 11 test IDs, 2 preview changes (102,210). D class counts angry56/happy49/neutral53/sad51; E angry52/happy52/neutral54/sad51. These are not known test corrections.

## Canonical completion gate

A user-downloadable standalone package `DEFHS_SYSTEM_E_CANONICAL_REPLAY_BUNDLE.zip` contains the unchanged original finalizer, authenticated D/E/semantic train archives, authentic test GPU archive, preview, and `run_canonical_production.sh`. Package SHA256 `d092d001280d164557fb8e90ca729afb59f10423182befb22fb50fd3404084a9`. **Not yet uploaded to GitHub.** WSL execution against `runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv` with SHA256 `1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469` is required to verify original 209 test WAV identities. The script fails if canonical-produced E candidate disagrees byte-for-byte with the preview.

After `CANONICAL_SYSTEM_E_CANDIDATE_REPLAY_PASS`, commit original finalizer source, resulting `Id,emotion` CSV, row-level probability audit, changes, and SHA manifest to this research branch, return to SS, **DO NOT submit**.

No public leaderboard score used in production; no protected validation or test labels accessed. System D remains public 0.88227 fallback.
