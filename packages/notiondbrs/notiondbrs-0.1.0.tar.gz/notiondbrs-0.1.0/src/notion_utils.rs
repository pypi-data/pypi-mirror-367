use std::collections::{BTreeMap, BTreeSet, HashMap};

use anyhow::{Result};
use notion_client::{
    endpoints::{
        Client,
        databases::query::{request::QueryDatabaseRequestBuilder, response::QueryDatabaseResponse},
        pages::create::request::CreateAPageRequest,
        search::title::{
            request::{Filter, SearchByTitleRequestBuilder, Sort, SortDirection, Timestamp},
            response::PageOrDatabase,
        },
    },
    objects::{database::DatabaseProperty, page::PageProperty, parent::Parent},
};

use notion_client::endpoints::databases::create::request::CreateADatabaseRequest;
use notion_client::objects::rich_text::{RichText, Text};

use crate::utils::chunk_into_vec_pages;

pub fn setup_notion_client(notion_token: &str) -> Result<Client> {
    let client = Client::new(notion_token.to_string(), None)?; //using the default reqwest client provided by notion_client crate
    //let db = client.databases.retreive_a_database(db_id).await?;
    println!("Connected to client");
    Ok(client)
}

pub async fn get_data_from_database(client: Client, db_id: &str) -> Result<QueryDatabaseResponse> {
    let request = QueryDatabaseRequestBuilder::default();

    let res = client
        .databases
        .query_a_database(db_id, request.build().unwrap())
        .await?;

    Ok(res)
}

pub async fn upsert_data_to_notion(
    client: Client,
    upload_data: BTreeMap<String, Vec<String>>,
    db_id: String,
) -> Result<()> {

    let notion_data = get_data_from_database(client.clone(), &db_id).await?;
    let notion_data_hashmap = crate::utils::convert_notion_result_to_hashmap(&notion_data)?;
    let merged_data: BTreeMap<String, Vec<String>>;

    if notion_data_hashmap.len() == 0 {
        merged_data  = upload_data.clone();
    } else {
        merged_data = crate::utils::compare_and_merge_btmaps(&upload_data, &notion_data_hashmap)?;
    }

    insert_data_to_notion(client, merged_data, db_id, false).await?;
    Ok(())
}

pub async fn insert_data_to_notion(
    client: Client,
    upload_data: BTreeMap<String, Vec<String>>,
    db_id: String,
    new_db: bool,
) -> Result<()> {
    let first_key = upload_data.keys().next().cloned();
    println!("{:#?} is the Key Column", first_key.clone().unwrap());
    let final_db_id: String;

    if new_db {
        final_db_id =
            create_database_using_pages(&client, &first_key, &upload_data, &db_id).await?;
    } else {
        final_db_id = db_id.to_string();
    }

    let chunked_pages = chunk_into_vec_pages(&upload_data);

    upload_data_parallel(&client, chunked_pages, &first_key, &final_db_id).await?;
    Ok(())
}

pub async fn create_database_using_pages(
    client: &Client,
    key_col: &Option<String>,
    upload_data: &BTreeMap<String, Vec<String>>,
    page_id: &str,
) -> Result<String> {
    let mut properties = BTreeMap::new();
    let columns: BTreeSet<_> = upload_data.keys().cloned().collect();

    for column in columns.iter() {
        let is_title = key_col.as_ref() == Some(column);

        let prop = if is_title {
            DatabaseProperty::Title {
                id: None,
                name: None,
                title: HashMap::new(),
            }
        } else {
            DatabaseProperty::RichText {
                id: None,
                name: None,
                rich_text: HashMap::new(),
            }
        };

        properties.insert(column.clone(), prop);
    }

    let request = CreateADatabaseRequest {
        parent: Parent::PageId {
            page_id: page_id.to_string(),
        },
        title: Some(vec![RichText::Text {
            text: Text {
                content: key_col.clone().unwrap_or_default(),
                link: None,
            },
            annotations: None,
            plain_text: None,
            href: None,
        }]),
        icon: None,
        cover: None,
        properties: properties,
    };

    let response = client.databases.create_a_database(request).await?;

    let new_db_id = response
        .id
        .clone()
        .ok_or_else(|| anyhow::anyhow!("Notion returned DB without id"))?;

    println!("New database created with ID : {:?}", new_db_id);
    Ok(new_db_id)
}
pub async fn upload_page(
    client: &Client,
    page: &BTreeMap<String, String>,
    key_col: &Option<String>,
    db_id: &str,
) -> Result<()> {
    let mut properties = BTreeMap::new();

    for (key, value) in page {
        let is_title = key_col.as_ref() == Some(key);

        let prop = if is_title {
            PageProperty::Title {
                id: None,
                title: vec![RichText::Text {
                    text: Text {
                        content: value.clone(),
                        link: None,
                    },
                    annotations: None,
                    plain_text: None,
                    href: None,
                }],
            }
        } else {
            PageProperty::RichText {
                id: None,
                rich_text: vec![RichText::Text {
                    text: Text {
                        content: value.clone(),
                        link: None,
                    },
                    annotations: None,
                    plain_text: None,
                    href: None,
                }],
            }
        };

        properties.insert(key.clone(), prop);
    }

    let request = CreateAPageRequest {
        parent: Parent::DatabaseId {
            database_id: db_id.to_string(),
        },
        icon: None,
        cover: None,
        children: None,
        properties,
    };

    client.pages.create_a_page(request).await?;
    Ok(())
}

pub async fn upload_data_parallel(
    client: &Client,
    pages: Vec<BTreeMap<String, String>>,
    key_col: &Option<String>,
    db_id: &str,
) -> Result<()> {

    println!("Upload started for {} items", pages.len());
    let mut handles = Vec::with_capacity(8);

    for page in pages {
        let cli = client.clone();
        let key = key_col.clone();
        let db = db_id.to_string();

        handles.push(tokio::spawn(async move {
            match upload_page(&cli, &page, &key, &db).await {
                Ok(_) => Ok(()),
                Err(e) => {
                    eprintln!("Upload page error: {:?}", e);
                    Err(e)
                }
            }
        }));
    }

    for task in handles {
        task.await??;
    }

    Ok(())
}

pub async fn get_all_databases(client: Client) -> Result<Vec<(String, String)>> {
    let mut request = SearchByTitleRequestBuilder::default();
    request.filter(Filter {
        value: notion_client::endpoints::search::title::request::FilterValue::Database,
        property: notion_client::endpoints::search::title::request::FilterProperty::Object,
    });
    request.sort(Sort {
        timestamp: Timestamp::LastEditedTime,
        direction: SortDirection::Ascending,
    });

    let response = client
        .search
        .search_by_title(request.build().unwrap())
        .await?;

    let databases = response
        .results
        .iter()
        .filter_map(|entry| {
            if let PageOrDatabase::Database(db) = entry {
                let id = db.id.clone().unwrap_or_default();
                let name = db
                    .title
                    .get(0)
                    .and_then(|text_block| text_block.plain_text().clone())
                    .unwrap_or_else(|| "<Untitled>".to_string());
                Some((id, name))
            } else {
                None
            }
        })
        .collect();

    Ok(databases)
}
