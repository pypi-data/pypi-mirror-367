use anyhow::{Result, bail};
use notion_client::endpoints::databases::query::response::QueryDatabaseResponse;
use notion_client::objects::page::PageProperty;
use std::collections::{BTreeMap, BTreeSet};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

pub fn convert_notion_result_to_hashmap(
    result: &QueryDatabaseResponse,
) -> Result<BTreeMap<String, Vec<String>>> {
    let mut data: BTreeMap<String, Vec<String>> = BTreeMap::new();

    for page in result.results.iter() {
        for (prop_name, prop_val) in &page.properties {
            let val = match prop_val {
                PageProperty::Title {
                    id: _,
                    title: title_arr,
                } => title_arr
                    .iter()
                    .filter_map(|t| t.plain_text().clone())
                    .collect::<Vec<String>>(),
                PageProperty::RichText {
                    id: _,
                    rich_text: rich_text_arr,
                } => rich_text_arr
                    .iter()
                    .filter_map(|rt| rt.plain_text().clone())
                    .collect::<Vec<String>>(),
                PageProperty::Number {
                    id: _,
                    number: number_arr,
                } => {
                    vec![
                        number_arr
                            .as_ref()
                            .map_or(" ".to_string(), |n| n.to_string()),
                    ]
                }
                _ => vec![" ".to_string()],
            };

            data.entry(prop_name.clone())
                .or_insert_with(Vec::new)
                .extend(val);
        }
    }

    Ok(data)
}

pub fn convert_pydict_to_hashmap(
    pydata: &Bound<'_, PyDict>,
) -> Result<BTreeMap<String, Vec<String>>> {
    let mut hashmap_data: BTreeMap<String, Vec<String>> = BTreeMap::new();

    for (key, value) in pydata.iter() {
        let key_str = key.extract::<String>()?;

        let py_list = value
            .downcast::<PyList>()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let rust_vec: Vec<String> = py_list
            .iter()
            .map(|item| item.extract::<String>())
            .collect::<PyResult<_>>()?;

        hashmap_data.insert(key_str, rust_vec);
    }

    Ok(hashmap_data)
}

pub fn chunk_into_vec_pages(
    upload_data: &BTreeMap<String, Vec<String>>,
) -> Vec<BTreeMap<String, String>> {
    let first_key = upload_data.keys().next().cloned();
    let page_count = first_key
        .as_ref()
        .and_then(|k| upload_data.get(k))
        .map(|v| v.len())
        .unwrap_or(0);
    let keys: BTreeSet<_> = upload_data.keys().cloned().collect();

    (0..page_count)
        .map(|idx| {
            let mut props = BTreeMap::new();
            for key in &keys {
                let val = upload_data
                    .get(key)
                    .and_then(|v| v.get(idx))
                    .cloned()
                    .unwrap_or_default();
                props.insert(key.clone(), val);
            }
            props
        })
        .collect()
}

pub fn compare_and_merge_btmaps(
    upload_data: &BTreeMap<String, Vec<String>>,
    existing_data: &BTreeMap<String, Vec<String>>,
) -> Result<BTreeMap<String, Vec<String>>> {
    let mut merged_data = BTreeMap::new();

    let first_key = existing_data.keys().next().cloned();
    let page_count_update = first_key
        .as_ref()
        .and_then(|k| upload_data.get(k))
        .map(|v| v.len())
        .unwrap_or(0);

    let page_count_existing = first_key
        .as_ref()
        .and_then(|k| existing_data.get(k))
        .map(|v| v.len())
        .unwrap_or(0);

    let columns_upload_data: BTreeSet<_> = upload_data.keys().cloned().collect();
    let columns_existing_data: BTreeSet<_> = existing_data.keys().cloned().collect();

    let missing: BTreeSet<_> = columns_existing_data
        .difference(&columns_upload_data)
        .cloned()
        .collect();

    if missing.is_empty() {
        let title_col_upload_data = first_key
            .as_ref()
            .and_then(|k| upload_data.get(k))
            .cloned()
            .unwrap_or_default();
        let title_col_existing_data = first_key
            .as_ref()
            .and_then(|k| existing_data.get(k))
            .cloned()
            .unwrap_or_default();

        println!(
            "new row num : {}, Existing row num : {}",
            page_count_update, page_count_existing
        );
        for idx in 0..page_count_update {
            let upload_data_val = title_col_upload_data.iter().nth(idx);
            if !title_col_existing_data.contains(&upload_data_val.unwrap()) {
                for key in &columns_existing_data {
                    let val = upload_data
                        .get(key)
                        .and_then(|v| v.get(idx))
                        .cloned()
                        .unwrap_or_default();
                    merged_data
                        .entry(key.clone())
                        .or_insert_with(Vec::new)
                        .push(val);
                }
            }
        }
        return Ok(merged_data.clone());
    } else {
        bail!("Missing values: {:?}", missing);
    }
}
