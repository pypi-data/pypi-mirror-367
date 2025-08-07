# MkDocs IDM Theme

A custom MkDocs theme for the Institute for Disease Modeling, based on Material for MkDocs with enhanced features for scientific documentation.

## Installation

Install the theme using pip:

```bash
pip install mkdocs-idm
```

## Usage

Add the theme to your `mkdocs.yml` by starting with the [template](https://github.com/gatesfoundation/mkdocs-idm/blob/main/mkdocs.yml) provided on github.

Note that you'll also need to setup the structure of the site under the `nav` section and update a few links (search for `TODO` in the template). 

## Documentation

For detailed documentation and examples, visit the [sharepoint](https://bmgf.sharepoint.com/:f:/s/IDMSoftwareTeam/EpvoFk_Pf21HngvuaqLXJykBR6ubMwOJ0qMj6tmbDGX5tA?e=Vg8deQ)

---

# MkDocs Templates and Guidance

This content is shared from the README into the "MkDocs Introduction" topic using `include-markdown`. This folder is set up both to introduce you to the syntax and build processes for Material with MkDocs and provide standard configuration and templates for setting up a new documentation set. This folder contains all the source files needed to build HTML docs with MkDocs and host them on GH-Pages. We recommend placing all files in the repository you want to document and updating the Markdown and mkdocs.yml files as needed.

For MkDocs, the mkdocs.yml file controls most aspects of the documentation build, style, table of contents, and plug-in functionality. The minimal files under customization/ are needed to meet GF requirements and should not require frequent updates. Avoid adding any other CSS or Javascript customization as it makes the doc build fragile and difficult to maintain consistency. For more information, see the [MkDocs documentation](https://squidfunk.github.io/mkdocs-material/reference/).

## README guidance

In the package README, include the following:

* An overview of the package and its usage
* Installation instructions
* A link to the hosted documentation at https://docs.idmod.org/project
* Package structure overview
* Disclaimer/license

## Doc builds and previews

You should build or preview the documentation locally before submitting documentation changes. 

### Preview the docs in a browser

1. Run a local server with:
   ```
   mkdocs serve --watch .
   ```
   
    The `watch` option will rebuild on changes outside the docs/ folder, such as docstring changes. 

2. Open a browser window at http://127.0.0.1:8000/<project>. This will rebuild to reflect changes each time a source file is updated and saved. 

### Build the docs 

1.  Build the documents:
    ```
    mkdocs build
    ```
2.  The built documents will be in `site/`.

## Hosting

Under .github/ there are GH-Actions files for running a test doc build when PRs are opened and pushing changes to GH-Pages when PRs are merged. The default URL for GH-Pages is org.github.io/repo, but when documentation is ready to share broadly, you should set up a custom domain following the URL structure docs.idmod.org/project (and specify this in mkdocs.yml). For more information, see [GitHub Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site). Coordinate with the research content team to add the CNAME record and set up a link on the [docs.idmod.org](https://docs.idmod.org/) landing page and a tool page on [idmod.org ](https://www.idmod.org/tools/). 

## Style guidance

### Microsoft Manual of Style

At IDM, we generally follow the [Microsoft Manual of Style](https://learn.microsoft.com/en-us/style-guide/welcome/) (MSTP). A few of the most notable rules to be aware of are listed below.

*  Use imperative verbs for tutorial and how to titles, no gerunds. "Get Started" not "Getting Started."
*  Use the Oxford comma (serial comma).
*  Don't use "should"--it's ambiguous. Rather, say a user must do something
   or that a computer/system will do something.
*  Verb tense and voice
   *  In general, use present tense and active voice.
   *  Use primarily second-person (you).
   *  Use first-person (I or we) sparingly. For example, "We recommend…" is more natural
      than "It is recommended that."
*  Be direct and use simple sentence structure.
   *  Avoid jargon.
   *  Don't use i.e. or e.g. as they can cause problems for non-native English speakers or machine translation.

Tutorial/how to guidelines are extensive (see chapter 6.) The primary points to follow are:

*  Sentences must provide the context and then the action. For example, "In the **Print**
   dialog box, click **All**."
*  Each step must encompass a single action, unless they are short and occur in the same place.
*  Additionally, you "click", you don't "click on."
*  Generally avoid using "please" and "thank you."
*  Use imperative mood verbs. In other words, verbs should take the form of commands. For example, "Enter your password" not "The user enters their password."
*  Consecutive list items should be separated by **>** and not **,**. For example, "Select **Explore > Experiments**".

### Differences from MSTP

Our house style guide differs from MSTP guidance in the following ways:

* Use title case (major words capitalized) for topic titles. 
* Use sentence case (only the first word and proper nouns capitalized) for section headings.
* Use bold, not italics, for parameter names.
* Parameter values, which are often in all-caps, are in plain text.
* Surround placeholder text with angle brackets.
* For example, text where users are expected to enter their username C:/Users/<username>.
* Italicize species names. For example, *A. funestus* and *A. gambiae*.
  
    * A note on mosquito names: for scientific naming convention, the first time you mention a species you give its full name (*Anopheles funestus*), and then the second time you can abbreviate the genus (*A. funestus*). However, there are two "A" mosquito genera that are commonly discussed in the disease literature (*Aedes* and *Anopheles*), so it's convention to use the first two letters of the genus name when abbreviating: *An. funestus* and *Ae. aegypti*. For pretty much every other category of organism, you'll just use the first letter and not the first two.
## Migrating existing content from Sphinx

* ChatGPT and Copilot work reasonably well to convert existing RST files to Markdown. Carefully review the output for any remaining issues, however. Documentation migrations are often a good time to review the content of the docs and not just the format. 
* Links use a different format. 
  
    * General links specify the link text manually rather than being generated from the topic title, so be sure to check that link text and topic titles stay in sync. 
    ```
    [link text](URL/relative path)
    ```
    * For Python objects, the link format will need to be updated from Sphinx syntax to MkDocs syntax:
    ```
    :py:func:`add_drug_campaign` to 
    [Arr][starsim.Arr]
    ```
    * Instead of intersphinx to link to other package objects, use mkdocstrings [inventories](https://mkdocstrings.github.io/python/usage/#inventories).
  
* Headings and titles use pound signs instead of underlining. In docstrings, the additional formatting around the Examples heading needed for Sphinx is no longer necessary.
* Instead of `literalinclude` or `include` directives to reuse content, use [snippets](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/). 
* Including math with LaTeX no longer requires a separate installation. Use $\beta$ for inline math and the following for blocks:
    $$
    \int_a^b f(x) dx = F(b) - F(a)
    $$
* Paragraphs with text lines with more than two trailing spaces will create a soft break, so we recommend pulling paragraphs on a single line or configuring your editor to trim trailing spaces to avoid inadvertent breaks. 