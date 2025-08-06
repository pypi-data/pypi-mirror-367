<h1 align="center">
<br>
<a href="https://sinapsis.tech/">
  <img
    src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true"
    alt="" width="300">
</a><br>
Sinapsis Docling
<br>
</h1>

<h4 align="center">Templates for simple and custom document conversion using Docling</h4>

<p align="center">
<a href="#installation">🐍 Installation</a> •
<a href="#features"> 🚀 Features</a> •
<a href="#example"> 📚 Usage example</a> •
<a href="#documentation">📙 Documentation</a> •
<a href="#license">🔍 License</a>
</p>

This **Sinapsis Docling** package provides templates for integrating, configuring, and running document conversion workflows powered by [Docling](https://docling-project.github.io/docling/).

<h2 id="installation">🐍 Installation</h2>


> [!IMPORTANT]
> Sinapsis project requires Python 3.10 or higher.
>

Install using your favourite package manager. We strongly encourage the use of <code>uv</code>, although any other package manager should work too.
If you need to install <code>uv</code> please see the [official documentation](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).


Example with <code>uv</code>:
```bash
  uv pip install sinapsis-docling --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-docling --extra-index-url https://pypi.sinapsis.tech
```

<h2 id="features">🚀 Features</h2>

<h3>Templates Supported</h3>

- **DoclingSimpleConversion**: Template for simple document conversions using the Docling framework.

    <details>
    <summary>Attributes</summary>

    - `convert_options`(Optional): Configuration for document conversion, such as error handling, page range, and file size limits (default: `{}`).
    - `export_format`(Optional): Format for document export (default: `export_to_markdown`). Options: `export_to_dict`, `export_to_doctags`, `export_to_element_tree`, `export_to_html`, `export_to_markdown`,`export_to_text`.
    - `image_mode`(Optional): Image handling mode (default: `placeholder`). Options: `placeholder`, `embedded`, `referenced`.
    - `output_dir`(Optional): Directory for saving the converted document(s) (default: `SINAPSIS_CACHE_DIR/docling/documents`).
    - `save_in_container`(Optional): Whether to store the converted document(s) in the container (default: `True`).
    - `save_locally`(Optional): Whether to save the converted document(s) locally (default: `False`).
    - `save_format`(Optional): Format for saving the document(s) (default: `save_as_markdown`). Options: `save_as_doctags`, `save_as_html`, `save_as_json`, `save_as_markdown`, `save_as_yaml`.
    - `path_to_doc`(Required): The source document(s) to convert. This can be a file path, a URL, or a list of file paths or URLs (default: `None`).

    </details>

- **DoclingCustomConversion**: Template for advanced document conversions using the Docling framework.

    <details>
    <summary>Attributes</summary>

    - `accelerator_options`(Optional): Options for the accelerator, including `num_threads`, `device`, `cuda_use_flash_attention2` (default: `{}`).
    - `convert_options`(Optional): Configuration for document conversion, such as error handling, page range, and file size limits (default: `{}`).
    - `export_format`(Optional): Format for document export (default: `export_to_markdown`). Options: `export_to_dict`, `export_to_doctags`, `export_to_element_tree`, `export_to_html`, `export_to_markdown`,`export_to_text`.
    - `image_mode`(Optional): Image handling mode (default: `placeholder`). Options: `placeholder`, `embedded`, `referenced`.
    - `ocr_engine`(Optional): OCR engine to use (default: `easyocr`). Options: `easyocr`, `ocrmac`, `rapidocr`, `tesserocr`, `tesseract`.
    - `ocr_options`(Optional): OCR engine configuration options (default: `{}`).
    - `output_dir`(Optional): Directory for saving the converted document(s) (default: `SINAPSIS_CACHE_DIR/docling/documents`).
    - `pipeline_options`(Optional): Conversion pipeline options (default: `{}`).
    - `save_in_container`(Optional): Whether to store the converted document(s) in the container (default: `True`).
    - `save_locally`(Optional): Whether to save the converted document(s) locally (default: `False`).
    - `save_format`(Optional): Format for saving the document(s) (default: `save_as_markdown`). Options: `save_as_doctags`, `save_as_html`, `save_as_json`, `save_as_markdown`, `save_as_yaml`.
    - `path_to_doc`(Required): The source document(s) to convert. This can be a file path, a URL, or a list of file paths or URLs (default: `None`).

    For detailed documentation on setting accelerator, OCR, and pipeline options, refer to the [Docling reference](https://docling-project.github.io/docling/reference/pipeline_options/).

    </details>



> [!TIP]
> Use CLI command ```sinapsis info --example-template-config TEMPLATE_NAME``` to produce an example Agent config for the Template specified in ***TEMPLATE_NAME***.

For example, for ***DoclingCustomConversion*** use ```sinapsis info --example-template-config DoclingCustomConversion``` to produce an example config like:

<details>
<summary ><strong><span style="font-size: 1.0em;">Config</span></strong></summary>

```yaml
agent:
  name: my_test_agent
templates:
- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}
- template_name: DoclingCustomConversion
  class_name: DoclingCustomConversion
  template_input: InputTemplate
  attributes:
    convert_options:
      headers: null
      raises_on_error: true
      max_num_pages: 90
      max_file_size: 1000
      page_range:
      - 1
      - 90
    export_format: export_to_markdown
    image_mode: placeholder
    output_dir: ~.cache/sinapsis/docling/documents
    save_in_container: true
    save_locally: false
    save_format: save_as_markdown
    path_to_doc: 'document.pdf'
    accelerator_options:
      num_threads: 4
      device: auto
      cuda_use_flash_attention2: false
    ocr_engine: easyocr
    ocr_options: 
    pipeline_options:
      create_legacy_output: true
      document_timeout: null
      accelerator_options:
        num_threads: 4
        device: auto
        cuda_use_flash_attention2: false
      enable_remote_services: false
      allow_external_plugins: false
      artifacts_path: null
      images_scale: 1.0
      generate_page_images: false
      generate_picture_images: false
      do_table_structure: true
      do_ocr: true
      do_code_enrichment: false
      do_formula_enrichment: false
      do_picture_classification: false
      do_picture_description: false
      force_backend_text: false
      table_structure_options:
        do_cell_matching: true
        mode: accurate
      ocr_options:
        lang: '`replace_me:typing.List[str]`'
        force_full_page_ocr: false
        bitmap_area_threshold: 0.05
      picture_description_options:
        batch_size: 8
        scale: 2
        picture_area_threshold: 0.05
      generate_table_images: false
      generate_parsed_pages: false

```
</details>

<h2 id='example'>📚 Usage example</h2>

This example shows how to use the **DoclingCustomConversion** template to export and save PDF files as Markdown.

<details>
<summary ><strong><span style="font-size: 1.4em;">Config</span></strong></summary>

```yaml
agent:
  name: documet_conversion
  description: document conversion agent using docling

templates:

- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}

- template_name: DoclingCustomConversion
  class_name: DoclingCustomConversion
  template_input: InputTemplate
  attributes:
    export_format: export_to_markdown
    save_locally: True
    save_format: save_as_markdown
    path_to_doc: ["https://arxiv.org/pdf/2408.09869", "https://arxiv.org/pdf/2206.01062"]
    pipeline_options:
      do_ocr: True
      do_table_structure: True
      force_full_page_ocr: True
      table_structure_options:
        do_cell_matching: False
      accelerator_options:
        num_threads: 8
    ocr_options:
      lang: ["es"]

```
</details>

This configuration defines an **agent** and a sequence of **templates** for document conversion, using Docling.

To run the config, use the CLI:
```bash
sinapsis run name_of_config.yml
```

<h2 id="documentation">📙 Documentation</h2>

Documentation is available on the [sinapsis website](https://docs.sinapsis.tech/docs)

Tutorials for different projects within sinapsis are available at [sinapsis tutorials page](https://docs.sinapsis.tech/tutorials)

<h2 id="license">🔍 License</h2>

This project is licensed under the AGPLv3 license, which encourages open collaboration and sharing. For more details, please refer to the [LICENSE](LICENSE) file.

For commercial use, please refer to our [official Sinapsis website](https://sinapsis.tech) for information on obtaining a commercial license.



