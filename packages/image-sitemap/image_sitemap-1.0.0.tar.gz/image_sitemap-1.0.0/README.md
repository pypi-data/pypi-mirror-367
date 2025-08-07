# image_sitemap
Image Sitemap Generator SEO tool.

Sitemap Images is a Python tool that generates [a specialized XML sitemap file](./example_sitemap_images.xml),
allowing you to submit image URLs to search engines like Google, Bing, and Yahoo.
This tool helps improve image search visibility, driving more traffic to your website and increasing engagement.
To ensure search engines can discover your sitemap, simply add the following line to your **robots.txt** file:
```txt
Sitemap: https://example.com/sitemap-images.xml
```
By including image links in your sitemap and referencing it in your robots.txt file, you can enhance your website's SEO and make it easier for users to find your content.

Google image sitemaps standard description - [Click](https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps).

## Examples

1. Set website page and crawling depth, run script
    ```python
    import asyncio
    
    from src.image_sitemap import Sitemap
    from src.image_sitemap.instruments.config import Config
      
    images_config = Config(
        max_depth=3,
        accept_subdomains=True,
        is_query_enabled=False,
        file_name="sitemap_images.xml",
        header={
           "User-Agent": "ImageSitemap Crawler",
           "Accept": "text/html",
        },
    )
    sitemap_config = Config(
        max_depth=3,
        accept_subdomains=True,
        is_query_enabled=False,
        file_name="sitemap.xml",
        header={
           "User-Agent": "ImageSitemap Crawler",
           "Accept": "text/html",
        },
    )
    
    asyncio.run(Sitemap(config=images_config).run_images_sitemap(url="https://rucaptcha.com/"))
    asyncio.run(Sitemap(config=sitemap_config).run_sitemap(url="https://rucaptcha.com/"))
    ```
2. Get sitemap images data in file 
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
        <url>
            <loc>https://rucaptcha.com/proxy/residential-proxies</loc>
            <image:image>
                <image:loc>https://rucaptcha.com/dist/web/assets/rotating-residential-proxies-NEVfEVLW.svg</image:loc>
            </image:image>
        </url>
    </urlset>
    ```

You can check examples file here - [Click](./example_sitemap_images.xml).
