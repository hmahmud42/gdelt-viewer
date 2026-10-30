from IPython import embed
embed()

from gdeltdoc import GdeltDoc, Filters

f = Filters(
    keyword = "climate change",
    start_date = "2020-05-10",
    end_date = "2020-05-11"
)

gd = GdeltDoc()

# Search for articles matching the filters
try:
    articles = gd.article_search(f)
except Exception as f:
    v = f



# # Get a timeline of the number of articles matching the filters
# timeline = gd.timeline_search("timelinevol", f)


