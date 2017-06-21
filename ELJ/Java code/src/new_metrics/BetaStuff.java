package new_metrics;
import java.io.IOException;
import java.nio.*;
import java.nio.file.*;
import java.util.Vector;
import serialization.*;

import org.apache.commons.math3.*;
import org.apache.commons.math3.distribution.*;
import org.apache.commons.math3.util.FastMath;

public class BetaStuff implements VoteCounts {
		
	public static void main(String[] ss) throws IOException {
		Metrics.use_var_shrinkage = true;
		Metrics.var_shrinkage = 0.003721;
		Metrics actual = new Metrics(
				wi_actual_dem,wi_actual_rep,
				//wi_fair_dem,wi_fair_rep,
				//wi_maxrep_dem,wi_maxrep_rep,
				8
				);
		/*
		Metrics maxrep = new Metrics(
				//wi_actual_dem,wi_actual_rep,
				//wi_fair_dem,wi_fair_rep,
				wi_maxrep_dem,wi_maxrep_rep,
				8
				);
		

		
		Metrics fair = new Metrics(
				//wi_actual_dem,wi_actual_rep,
				wi_fair_dem,wi_fair_rep,
				//wi_maxrep_dem,wi_maxrep_rep,
				8
				);
		Metrics maxdem = new Metrics(
				//wi_actual_dem,wi_actual_rep,
				//wi_fair_dem,wi_fair_rep,
				wi_maxdem_dem,wi_maxdem_rep,
				8
				);
				*/
		
		

		
		if( true) {
			actual.num_districts = 99;
			Vector<GammaDistribution> district_gammas = actual.district_gammas;

			String contents = new String(Files.readAllBytes(Paths.get("wi.json")));
			DefaultJSONObject json = new DefaultJSONObject(contents);
			System.out.println(json.toJSON());
			
			actual.district_betas = new Vector<BetaDistribution>();
			actual.district_gammas = new Vector<GammaDistribution>();			
			int i = 0;
			for( JSONObject o : (Vector<JSONObject>)json.getVector("district_vote")) {
				actual.district_betas.add(new BetaDistribution(o.getDouble("alpha"),o.getDouble("beta")));
				actual.district_gammas.add(district_gammas.get(i % district_gammas.size()));
				i++;
			}
			
			actual.centered_district_betas = new Vector<BetaDistribution>();
			for( JSONObject o : (Vector<JSONObject>)json.getVector("centered_district_vote")) {
				actual.centered_district_betas.add(new BetaDistribution(o.getDouble("alpha"),o.getDouble("beta")));
			}
			
			JSONObject e = json.getObject("popular_vote");
			actual.election_betas = new BetaDistribution(e.getDouble("alpha"),e.getDouble("beta"));
		}
		
				
		actual.showBetas();
		System.out.println("done 0");
		actual.computeSeatProbs(false);
		actual.showSeats();
		//actual.computeAsymmetry(false);
		//actual.showAsymmetry();
		System.out.println("done 1");
		//actual.showHistogram();
		System.out.println("done 2");
		
		//System.out.println("mid");
		//maxrep.showBetas();
		//fair.showBetas();
		//actual.showBetas();
		
		//actual.sh
		//maxdem.showBetas();
		
		//actual.showBetas();
		//actual.computeSeatProbs(true);
		//actual.showSeats();
		
		
		//actual.computeAsymmetry(true);
		//actual.showAsymmetry();
		//System.out.println("packing....");
		//actual.showPacking();

		//actual.showBetaParameters();
		//actual.showPacking();
		System.out.println("done 2");
		
		double[] dd = actual.getPC();
		System.out.println("ed: "+dd[0]);
		System.out.println("er: "+dd[1]);
		//actual.showHistogram();
		//fair.showHistogram();
		//maxdem.showHistogram();
		//maxrep.showHistogram();
	}



}