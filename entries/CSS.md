# CSS

# Cascading Style Sheets (CSS)

**Cascading Style Sheets (CSS)** is a stylesheet language used to describe the presentation of a document written in **HTML** or **XML** (including SVG, MathML, and XHTML). CSS defines how elements should be rendered on screen, paper, in speech, or on other media. It is one of the core technologies of the **World Wide Web**, alongside HTML and JavaScript.

## History
- CSS was first proposed in **1994** by **Håkon Wium Lie**, while working at CERN, to separate document structure from presentation.  
- The **World Wide Web Consortium (W3C)** developed CSS standards, with **Bert Bos** contributing significantly.  
- **CSS1** was released in **1996**, followed by **CSS2** in **1998**.  
- Later versions (often referred to as **CSS3**) were split into individual modules, each evolving separately.  

## Features
- **Selectors:** Target HTML elements to apply styles.  
- **Box model:** Defines how margins, borders, padding, and content interact.  
- **Layout systems:** Includes **Flexbox** and **CSS Grid** for complex designs.  
- **Styling capabilities:** Fonts, colors, spacing, animations, transitions, and responsive design.  
- **Cascading and specificity:** Rules determine which styles take precedence when multiple apply.  

## Types of CSS
1. **Inline CSS** – applied directly to HTML elements.  
2. **Internal CSS** – defined within a `<style>` tag in the HTML document.  
3. **External CSS** – stored in separate `.css` files and linked to HTML.  

## Example
```css
body {
  font-family: Arial, sans-serif;
  background-color: #f0f0f0;
}

h1 {
  color: darkblue;
  text-align: center;
}