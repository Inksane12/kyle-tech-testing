# Evaluation method

[Showcase](../index.html) · [RTX 4070 evaluation](../evaluation.html)

## General procedure

1. Define a practical question, product revision, procedure, repeat count, evidence and stop criteria before testing.
2. Record test-time hardware and software context. Distinguish owner-reported specifications from contemporaneous records.
3. Preserve original measurements and notes. Document timestamps, valid/missing samples, failures, interruptions and deviations.
4. Keep measured values, operator-reported details, subjective impressions and interpretation separate.
5. State the sample size and limits. A short test cannot establish long-term reliability; GPU utilization is not throughput; reported GPU power is not calibrated wall power.
6. Disclose product source, loan/gift/purchase status, payments, affiliate arrangements, return terms, manufacturer involvement, and material corrections.

## RTX 4070 capture specifics

The included CSVs use the published NVIDIA `nvidia-smi` logger schema. Each capture has 59 rows, approximately five seconds apart, and records UTC timestamp, GPU identity, driver version, temperature, GPU utilization, used/total memory, and driver-reported GPU power. The published report's full-capture arithmetic means and sample peaks were independently recomputed from these files. Polling jitter means these are sample averages, not time-weighted values. Each file covers a separate window; the captures are not simultaneous.

The owner-labeled idle baseline includes a 35% sampled utilization point. The mixed workload average includes idle periods and is not a generation-only statistic. Two completed ERNIE Image Turbo generations are owner-reported; no independent completion evidence, timing, resolution, batch size or exact workflow export was provided.

The captures represent about five minutes each. They are not an endurance test and do not measure output quality, throughput, whole-system energy, fan noise, clocks, throttle reasons, CPU temperature, or ambient conditions.

## Further test procedures

See the [main portfolio's first-test protocol](https://github.com/Inksane12/hardware-testing-portfolio/blob/main/methodology/FIRST_TEST.md) for a future controlled ComfyUI session. That protocol requires separate owner approval before any workload. The existing workflow is not changed and no test is started by this site. Peripherals and gaming reports are demonstrations only; no product outcomes are implied.
