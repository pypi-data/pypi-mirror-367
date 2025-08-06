use crate::error::{Result, XacroError};
use std::path::Path;
use xmltree::{Element, XMLNode};

pub fn parse_file(filename: &Path) -> Result<Element> {
    let content = std::fs::read_to_string(filename).map_err(XacroError::Io)?;

    parse_string(&content)
}

pub fn parse_string(xml_content: &str) -> Result<Element> {
    Element::parse(xml_content.as_bytes())
        .map_err(|e| XacroError::Parse(format!("XML parsing error: {e}")))
}

pub fn element_to_string(element: &Element) -> String {
    let mut output = Vec::new();
    element.write(&mut output).unwrap();
    String::from_utf8_lossy(&output).to_string()
}

pub fn find_child<'a>(element: &'a Element, tag_name: &str) -> Option<&'a Element> {
    for child in &element.children {
        if let XMLNode::Element(child_elem) = child {
            if child_elem.name == tag_name {
                return Some(child_elem);
            }
        }
    }
    None
}

pub fn find_child_mut<'a>(element: &'a mut Element, tag_name: &str) -> Option<&'a mut Element> {
    for child in &mut element.children {
        if let XMLNode::Element(child_elem) = child {
            if child_elem.name == tag_name {
                return Some(child_elem);
            }
        }
    }
    None
}

pub fn get_required_attr<'a>(element: &'a Element, attr_name: &str) -> Result<&'a String> {
    element
        .attributes
        .get(attr_name)
        .ok_or_else(|| XacroError::Parse(format!("Missing required attribute: {attr_name}")))
}

pub fn get_optional_attr<'a>(element: &'a Element, attr_name: &str) -> Option<&'a String> {
    element.attributes.get(attr_name)
}

pub fn remove_children_by_name(element: &mut Element, tag_name: &str) {
    element.children.retain(|child| {
        if let XMLNode::Element(child_elem) = child {
            child_elem.name != tag_name
        } else {
            true
        }
    });
}

pub fn replace_element_content(target: &mut Element, source: Element) {
    target.children = source.children;
    target.attributes = source.attributes;
    target.namespace = source.namespace;
    target.prefix = source.prefix;
    target.name = source.name;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_xml() {
        let xml = r#"<root><child attr="value">text</child></root>"#;
        let element = parse_string(xml).unwrap();
        assert_eq!(element.name, "root");
        assert_eq!(element.children.len(), 1);
    }

    #[test]
    fn test_find_child() {
        let xml = r#"<root><child1/><child2/></root>"#;
        let element = parse_string(xml).unwrap();

        assert!(find_child(&element, "child1").is_some());
        assert!(find_child(&element, "child2").is_some());
        assert!(find_child(&element, "child3").is_none());
    }

    #[test]
    fn test_get_attributes() {
        let xml = r#"<root required="yes" optional="maybe"/>"#;
        let element = parse_string(xml).unwrap();

        assert!(get_required_attr(&element, "required").is_ok());
        assert!(get_required_attr(&element, "missing").is_err());

        assert!(get_optional_attr(&element, "optional").is_some());
        assert!(get_optional_attr(&element, "missing").is_none());
    }
}
