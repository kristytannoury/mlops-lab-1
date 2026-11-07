# Lab 5 — CI/CD with GitHub Actions

## Questions

### 1. Why should a unit test not load the real MLflow model?

The test would depend on the MLflow server, its network connection, and the model artifact being available. It could also start failing if the `champion` alias moved to a model with different outputs, even when the API code was correct. Loading a real model is slower and makes the test depend on external state.

### 2. What does the fake-model API test prove?

It proves that the API accepts and decodes an uploaded image, calls the configured model interface, and returns JSON with the expected category field and a confidence in range. It does not prove that the real model loads, predicts correctly, or has good accuracy.

### 3. Which check catches a train/test duplicate, and why is it dangerous?

The MD5 content-hash check catches identical image bytes in different splits. A duplicate can leak training examples into evaluation and make the reported evaluation score look better than performance on unseen data. A corrupted image usually causes a visible decoding or training error; a duplicate can silently produce misleading results.

Running the validator on the existing `food11_processed_mini` dataset reports cross-split duplicates (43 duplicate pairs in the current data), so the dataset currently fails this contract check.

### 4. Where should data validation run if GitHub cannot see the DVC data?

Run it locally after pulling the DVC dataset and before training. Also run it in the data preparation or ingestion pipeline on a machine that has access to the DVC remote, before publishing the processed dataset. A CI workflow can run it too if that workflow is configured to pull the data from an accessible remote.

### 5. What does `needs: test` do for the smoke job?

If `test` fails, GitHub Actions skips `smoke` because it depends on `test`. Without `needs`, the jobs can run independently, so `smoke` could run even when the unit tests failed.

### 6. How long did the workflow take, and what got faster on the second run?

The successful `main` run took about 4 minutes 48 seconds (run [42388822023](https://github.com/kristytannoury/mlops-lab-1/actions/runs/42388822023)), including the image-push job. A repeat on a feature branch took about 1 minute 16 seconds, but it skipped the `push` job by design, so the total times are not directly comparable. `uv sync` took 3 seconds on the first successful run and 4 seconds on the repeat; it did not measurably get faster. The CI cache was already warm, so dependency setup stayed brief.

### 7. Why tag the image with the commit SHA instead of `latest`?

The commit SHA identifies the exact source revision used to build the image and remains a stable tag. With `latest`, one machine may pull it before a new image is pushed while another pulls it afterward; both machines then use the tag `latest` but run different code. A locally cached `latest` can also differ from the current registry version.

### 8. Why declare `permissions` on the image-push job?

Explicit permissions give the job only the access it needs: read repository contents and write packages. If a compromised step received broad write access, it could modify repository contents or other writable resources using the run token. Restricting the token limits the damage it could do.

## Local verification

- `uv run ruff check src tests`: passed.
- `uv run pytest -q`: 5 passed.
- `uv run python src/food11/validate_data.py data/food11_processed_mini`: folder, image, minimum-count, and class-share checks passed; duplicate-image check failed on existing cross-split duplicates.
