package new_metrics;

public class ComputePacking {

	public double[] get_packing(double[][] district_votes) {
		
		//normalize votes to 50/50.
		double sum_d = 0;
		double sum_r = 0;
		double[][] centered_district_votes = new double[district_votes.length][2];
		for( int i = 0; i < district_votes.length; i++) {
			sum_d += district_votes[i][0];
			sum_r += district_votes[i][1];
		}
		double target = (sum_d+sum_r)/2;
		for( int i = 0; i < district_votes.length; i++) {
			centered_district_votes[i][0] = district_votes[i][0] * target / sum_d;
			centered_district_votes[i][1] = district_votes[i][1] * target / sum_r;
		}
		
		//count disenfranchisement
		double dem_sq = 0; 
		double rep_sq = 0;
		double tot = 0;
		for( int i = 0; i < district_votes.length; i++) {
			double excess = centered_district_votes[i][0] - centered_district_votes[i][1];
			if( excess < 0) {
					rep_sq += excess * excess;
			} else {
					dem_sq += excess * excess;
			}
			tot += Math.abs(excess);
		}
		if( tot == 0) { tot = 1; }
		
		return new double[]{dem_sq/tot,rep_sq/tot,dem_sq/target,rep_sq/target,target};
	}

}
