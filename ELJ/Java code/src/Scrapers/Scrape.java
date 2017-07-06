import java.net.*;
import java.io.*;

public class Scrape {
	public static void main(String[] args) {
		for( int fips = 1; fips < 60; fips++) {
			try {
				String url = "http://uselectionatlas.org/RESULTS/compare.php?year=2016&fips="+fips+"&f=1&off=0&elect=0&type=state";
				String data = getUrlContents(url);
				//System.out.println("l: "+data.length());
				String[] rows = data.split("<tr id");
				for( int i = 1; i < rows.length; i++) {
					String[] cols = rows[i].split("<td");
					//System.out.println("c "+i);
					//System.out.println("00"+cols[0]);
					String id = cols[0].split("\"")[1];
					//System.out.println("id: "+id);
					for( int j = 1; j < cols.length; j++) {
						try {
						//System.out.println(".");
						cols[j] = cols[j].substring(cols[j].indexOf(">")+1);
						//System.out.println("o");
						cols[j] = cols[j].substring(0,cols[j].indexOf("</td>")).trim();
						//System.out.print("0"+j+" "+cols[j]+"\t");
						} catch (Exception ex) {
							//ex.printStackTrace();
							continue;
						}
					}
					String dem = cols[10].substring(0, cols[10].indexOf("&"));
					String rep = cols[11].substring(0, cols[11].indexOf("&"));
					System.out.println(fips+","+id+","+dem+","+rep);
				}
			} catch (Exception ex) {
				ex.printStackTrace();
				continue;
			}
		}
	}
	
	
	
	  private static String getUrlContents(String theUrl)
	  {
		System.setProperty("http.agent", "Chrome");
	    StringBuilder content = new StringBuilder();

	    // many of these calls can throw exceptions, so i've just
	    // wrapped them all in one try/catch statement.
	    try
	    {
	      // create a url object
	      URL url = new URL(theUrl);

	      // create a urlconnection object
	      URLConnection urlConnection = url.openConnection();

	      // wrap the urlconnection in a bufferedreader
	      BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));

	      String line;

	      // read from the urlconnection via the bufferedreader
	      while ((line = bufferedReader.readLine()) != null)
	      {
	        content.append(line + "\n");
	      }
	      bufferedReader.close();
	    }
	    catch(Exception e)
	    {
	      e.printStackTrace();
	    }
	    return content.toString();
	  }
}
