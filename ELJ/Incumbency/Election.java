
public class Election {
	String state = "";
	String district = "";
	int cycle = 0;
	int year = 0;
	boolean contested = true;
	boolean on_year = false;
	double districtPVI = 0;
	
	double dem_raw = 0;
	double rep_raw = 0;
	
	//imputed if uncontested
	double dem_imputed = 0;
	double rep_imputed = 0;
	
	//imputed if uncontested, otherwise incumbency adjusted
	double dem_adj = 0;
	double rep_adj = 0;
	
	//centered, from adjusted votes
	double dem_centered = 0; 
	double rep_centered = 0;
	
	boolean dem_incu = false;
	boolean rep_incu = false;
	
	public String getStateDistrict() {
		return state+"-"+district;
	}
	
	public double getElectionPVI() {
		return dem_centered/(dem_centered+rep_centered);
	}
	public double getIncorrectWinner(double inc_effect, double popPVI) {
		double dem = districtPVI*popPVI;
		double rep = (1-districtPVI)*(1-popPVI);
		if(dem_incu) dem *= inc_effect;
		if(rep_incu) rep *= inc_effect;
		boolean predict_dem_win = dem > rep; 
		boolean actual_dem_win = dem_imputed > rep_imputed;
		return ((predict_dem_win && actual_dem_win) || (!predict_dem_win && !actual_dem_win)) ? 0.0 : 1.0;
	}
	
	public double getDelta() {
		return Math.abs(districtPVI - getElectionPVI());
	}
	public void fromLine(String s) {
		String[] ss = s.split(",");
		
		state = ss[C.State];
		district = ss[C.AreaNumber];
		year = Integer.parseInt(ss[C.raceYear]);
		cycle = (year-1) / 10;
		cycle = cycle*10;
		//System.out.println("year:"+year+" cycle:"+cycle);
		contested = ss[C.DemStatus].equals("Challenger") || ss[C.RepStatus].equals("Challenger");
		dem_raw = Double.parseDouble(ss[C.DemVotes]);
		rep_raw = Double.parseDouble(ss[C.RepVotes]);
		dem_imputed = Double.parseDouble(ss[C.imputedDem]);
		rep_imputed = Double.parseDouble(ss[C.imputedRep]);
		dem_incu = ss[C.DemStatus].equals("Incumbent");
		rep_incu = ss[C.RepStatus].equals("Incumbent");
		on_year = year % 4 == 0;
	}
	interface C {
		public static int id = 0;
		public static int State = 1;
		public static int raceYear = 2;
		public static int AreaNumber = 3;
		public static int RepVotes = 4;
		public static int RepStatus = 5;
		public static int DemVotes = 6;
		public static int DemStatus = 7;
		public static int DemVotePct = 8;
		public static int Winner = 9;
		public static int imputedRep = 10;
		public static int imputedDem = 11;
		public static int centeredRep = 12;
		public static int centeredDem = 13;
	}
}
