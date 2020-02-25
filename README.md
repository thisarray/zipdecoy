# ZIP Decoy

Some websites are just too thirsty for your ZIP code even when their information does not depend on location.
For example, large banks ask for your ZIP code upfront which makes me think they are doing something shady like
[redlining](https://en.wikipedia.org/wiki/Redlining).

If you are like me, you only know your own ZIP code and are hesitant to give it out for something trivial.
This is where ZIP Decoy comes in.
It returns a list of nearby ZIP codes that you can use instead of your real ZIP code.
They are close enough so location based results are similar to your actual ZIP code without having to give your real ZIP code.

ZIP Decoy runs entirely in your browser.
It does not track you or save anything.
Since it is a webpage on GitHub, it cannot do those things.

## Implementation notes

AKA. Things no one cares about except me.

### ZCTA

The ZIP codes in ZIP Decoy are based on the ZIP Code Tabulation Areas (ZCTA) from the
[United States Census Bureau](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html).

Technically, ZCTA are not the same as ZIP codes because they are based on the most frequent ZIP code in a census block which is combined with other blocks to create larger areas.

This difference actually works to our advantage because it anonymizes each address.
ZCTA contain multiple addresses so a single address cannot be uniquely identified.

### Haversine distance

The [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula) with the smaller polar radius of 3950 miles is used to calculate the great-circle distance between ZIP codes using their latitudes and longitudes.
Since the Earth is not a perfect sphere, the resulting distance is an approximation.
