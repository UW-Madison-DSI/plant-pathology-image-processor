# plant-pathology-image-processor
extract information from plant pathlogy images

> Setup and Execution

1. Create a virtual environment

```bash
conda create -n plant-pathology-image-processor python=3.9
```
2. Activate the virtual environment

```bash
conda activate plant-pathology-image-processor
```
3. Install the requirements

```bash
pip3 install -e .
```

4. Run the streamlit app

```bash
streamlit run src/leaflesiondetector/app.py
```

5. Requirement errors

If encountered `cannot import name 'TypeGuard' from 'typing_extensions'` in a conda environment, use `conda install -c pyviz hvplot`

![Demo](./demo.png)