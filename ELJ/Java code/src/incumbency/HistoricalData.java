import java.io.File;
import java.io.FileInputStream;
import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.Map.Entry;

import javax.swing.JFileChooser;

import java.util.Vector;

public class HistoricalData {
	Vector<Election> allElections = new Vector<Election>();
	HashMap<Integer,Vector<Election>> electionsByYear = new HashMap<Integer,Vector<Election>>();
	
	HashMap<Integer,Vector<Election>> electionsByCycle = new HashMap<Integer,Vector<Election>>();
	HashMap<Integer,HashMap<Integer,Vector<Election>>> electionsByCycleThenYear = new HashMap<Integer,HashMap<Integer,Vector<Election>>>();
	HashMap<Integer,HashMap<String,Vector<Election>>> electionsByCycleThenStateDistrict 
		= new HashMap<Integer,HashMap<String,Vector<Election>>>();

	
	public static void main(String[] ss) {
		String filename = "C:\\Users\\kbaas\\git\\UnburyTheLead\\ELJ\\Data\\congressImputed.csv";
		if( false) {
			JFileChooser jfc = new JFileChooser();
			int res = jfc.showOpenDialog(null);
			if( res != javax.swing.JFileChooser.APPROVE_OPTION) {
				return;
			}
			File f = jfc.getSelectedFile();
			filename = f.getAbsolutePath();
		}
		//HistoricalData d = new HistoricalData(filename,new int[]{1980});
		//HistoricalData d = new HistoricalData(filename,new int[]{1990});
		//HistoricalData d = new HistoricalData(filename,new int[]{2000});
		//HistoricalData d = new HistoricalData(filename,new int[]{2010});
		//HistoricalData d = new HistoricalData(filename,new int[]{1990,2000});
		HistoricalData d = new HistoricalData(filename,new int[]{2000,2010});
	}
	
	HistoricalData(String filename, int[] cycle) {
		loadElectionsFromCsv(filename);
		fillHashMaps();
		System.out.println(""+allElections.size());
		System.out.println(""+electionsByYear.size());
		System.out.println(""+electionsByCycle.size());
		System.out.println(""+electionsByCycleThenYear.size());
		System.out.println(""+electionsByCycleThenStateDistrict.size());
		
		plotIncumbency(cycle);
	}
	
	public void loadElectionsFromCsv(String filename) {
		String sin = fileToString(filename) ; //TODO: set file name ...congressImputed.csv
		//C:\Users\kbaas\git\UnburyTheLead\ELJ\Data\congressImputed.csv
		
		String[] lines = sin.split("\n");
		for(int i = 1; i < lines.length; i++ ) { //skip header row
			String line = lines[i];
			Election e = new Election();
			e.fromLine(line);
			allElections.add(e);
		}
	}

	public String fileToString(String filename) {
		System.out.println("getString(" + filename + ")");
		File f = new File(filename);
		if (!f.exists()) {
			return null;
		}
		byte[] y = null;
		int filesize = 0;
		try {
			FileInputStream fis = new FileInputStream(f);
			while( fis.available() > 0) {
				filesize = fis.available();
				y = new byte[filesize];
				fis.read(y);
			}
			fis.close();
		}
		catch (Exception ex) {
			System.out.println(ex);
			return null;
		}

		String s = new String(y);
		return s.trim();
	}

	public void fillHashMaps() {
		for( Election e : allElections) {
			{ //fill by year
				Vector<Election> y = electionsByYear.get(e.year);
				if( y == null) { y = new Vector<Election>(); electionsByYear.put(e.year,y); }
				y.add(e);
			}
			{ //fill by cycle
				Vector<Election> y = electionsByCycle.get(e.cycle);
				if( y == null) { y = new Vector<Election>(); electionsByCycle.put(e.cycle,y); }
				y.add(e);
			}
		}
		for( Entry<Integer,Vector<Election>> es : electionsByCycle.entrySet()) {
			
			{ //then by year
				HashMap<Integer,Vector<Election>> hm = new HashMap<Integer,Vector<Election>>();
				electionsByCycleThenYear.put(es.getKey(),hm);
				for( Election e : es.getValue()) {
					Vector<Election> y = hm.get(e.year);
					if( y == null) { y = new Vector<Election>(); hm.put(e.year,y); }
					y.add(e);
				}
			}

			{ //then by district
				HashMap<String,Vector<Election>> hm = new HashMap<String,Vector<Election>>();
				electionsByCycleThenStateDistrict.put(es.getKey(),hm);
				for( Election e : es.getValue()) {
					Vector<Election> y = hm.get(e.getStateDistrict());
					if( y == null) { y = new Vector<Election>(); hm.put(e.getStateDistrict(),y); }
					y.add(e);
				}
			}
		}
	}
	
	public void plotIncumbency(int[] cycle) {
		DecimalFormat df = new DecimalFormat("0.000");
		double min_val = 99999999999999999999999999999.9;
		double on_year = 0;
		double off_year = 0;
		double num_elections = 0;
		for( int i = 0; i < cycle.length; i++) {
			num_elections += electionsByCycle.get(cycle[i]).size();
		}
		for( double on_inc_test = 1.00; on_inc_test < 1.5; on_inc_test += 0.001) {
			//for( double off_inc_test = 1.05; off_inc_test < 1.25; off_inc_test += 0.002) {
			double off_inc_test = on_inc_test;
				double d = 0;
				double w = 0;
				for( int i = 0; i < cycle.length; i++) {
					
					//1 compute adjusted for all elections (using given incumbency %)
					computeAdjusted(electionsByCycle.get(cycle[i]), off_inc_test, on_inc_test);
					
					//2 compute mean center, per year
					for( Entry<Integer,Vector<Election>> e : electionsByCycleThenYear.get(cycle[i]).entrySet()) {
						meanCenter(e.getValue());
					}
					
					//3 compute cycle-district average
					for( Entry<String,Vector<Election>> e : electionsByCycleThenStateDistrict.get(cycle[i]).entrySet()) {
						computeDistrictPVI(e.getValue());
					}
					
					//4 compute total absolute deviation
					d += getTotalDeviation(electionsByCycle.get(cycle[i]),on_inc_test,0.50);
					w += getTotalIncorrects(electionsByCycle.get(cycle[i]),on_inc_test,0.50);
				}
				System.out.println(""+df.format(off_inc_test)+", "+(d/num_elections));
				if( d < min_val) {
					min_val = d;
					on_year = on_inc_test; 
					off_year = off_inc_test; 
					//System.out.println("new min: "+df.format(off_inc_test)+": "+df.format(on_inc_test)+": "+(d/num_elections)+": "+(w/num_elections));
				}
				//System.out.println(df.format(inc_test)+": "+d);
			//}
		}
	}

	public void computeAdjusted(Vector<Election> elections, double off_year_incumbency_multiplier, double on_year_incumbency_multiplier) {
		double on_incumbency_divisor = 1.0/ on_year_incumbency_multiplier;
		double off_incumbency_divisor = 1.0/ off_year_incumbency_multiplier;
		for( Election e : elections) {
			if( e.contested) {
				e.dem_adj = e.dem_raw * (e.dem_incu ? (off_incumbency_divisor): 1.0);
				e.rep_adj = e.rep_raw * (e.rep_incu ? ( on_incumbency_divisor): 1.0);
				//e.dem_adj = e.dem_raw * (e.dem_incu ? (e.on_year ? on_incumbency_divisor : off_incumbency_divisor): 1.0);
				//e.rep_adj = e.rep_raw * (e.rep_incu ? (e.on_year ? on_incumbency_divisor : off_incumbency_divisor): 1.0);
			} else {
				e.dem_adj = e.dem_imputed;
				e.rep_adj = e.rep_imputed;
			}
		}
	}
	
	public void meanCenter(Vector<Election> elections) {
		double dem_vote = 0;
		double rep_vote = 0;
		for( Election e : elections) {
			dem_vote += e.dem_adj;
			rep_vote += e.rep_adj;
		}
		
		double target = (dem_vote + rep_vote)/2.0;
		dem_vote = target/dem_vote;
		rep_vote = target/rep_vote;
		
		for( Election e : elections) {
			e.dem_centered = e.dem_adj * dem_vote;
			e.rep_centered = e.rep_adj * rep_vote;
		}
	}
	
	public void computeDistrictPVI(Vector<Election> elections) {
		double PVI = 0;
		for( Election e : elections) {
			PVI += e.dem_centered / (e.dem_centered + e.rep_centered);
		}
		PVI /= elections.size();
		for( Election e : elections) {
			e.districtPVI = PVI;
		}
	}
	
	
	public double getTotalDeviation(Vector<Election> elections, double inc, double pop) {
		double d = 0;
		for( Election e : elections) {
			d += e.getDelta(inc,pop);
		}
		return d;
	}
	public double getTotalIncorrects(Vector<Election> elections, double inc, double pop) {
		double d = 0;
		for( Election e : elections) {
			d += e.getIncorrectWinner(inc, pop);
		}
		return d;
	}
	

}
