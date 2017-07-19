package compare_measures.measures;

import java.util.Collections;
import java.util.Vector;

import util.Pair;

import compare_measures.Draw;
import compare_measures.IntegrationFunction;

public abstract class aMeasure implements iMeasure, IntegrationFunction {
	
	
	public double mean = 0;
	public double sd = 1;
	public double mad = 1;
	
	
	PiecewiseLinearMonotonicCurve score_curve = new PiecewiseLinearMonotonicCurve();

	public double f(double y, double dx) {
		return Math.log(y)*dx;
	}
	public double f(double x0,double x1,double y0,double y1) {
		if( false) {
			return (x1-x0)*(y0+y1)/2;
		}
		
		double a = (y1-y0)/(x1-x0);
		double b = y0 - a*x0;
		
		double axpb0 = y0;//a*x0+b;
		double axpb1 = y1;//a*x1+b;
		
		double upper = axpb1*Math.log(axpb1)/a - axpb1/a;
		double lower = axpb0*Math.log(axpb0)/a - axpb0/a;
		
		return upper-lower;
	}
	
	public double getSeatFraction(Draw draw, double pct) {
		double inverse_pct = 1.0-pct;
		double seats = 0.0;
		
		for( int i = 0; i < draw.centered_district_pcts.length; i++) {
			double rep = draw.centered_district_pcts[i];
			double dem = 1.0-draw.centered_district_pcts[i];
			if( rep*pct > dem*inverse_pct) {
				seats++;
			}

		}
		
		return (seats)/(double)draw.centered_district_pcts.length;
	}

	
	
	@Override
	public void scoreDraws(Vector<Draw> draws) {
		Vector<Pair<Double,Draw>> scores = new Vector<Pair<Double,Draw>>(); 
		for( Draw draw : draws) {
			scores.add(new Pair(getScore(draw),draw));
		}
		Collections.sort(scores);
		
		double sum = 0;
		mean = 0;
		
		double inc = 1.0/(double)scores.size();
		double cur = inc/2.0;
		score_curve.samples.add(new double[]{0,getLowerBound()});
		for( int i = 0; i < scores.size(); i++) {
			Pair<Double,Draw> score = scores.get(i);
			sum += score.a;
			score.b.scores.put(getAbbr(), score.a);
			score.b.scores.put(getAbbr()+" percentile", cur);
			score_curve.samples.add(new double[]{cur,score.a});
			cur += inc;
		}
		
		mean = sum/(double)scores.size();
		sd = 0;
		for( int i = 0; i < scores.size(); i++) {
			double d = scores.get(i).a;
			sd += d*d;
			mad += Math.abs(d);
		}
		sd /= ((double)scores.size()-1.0);
		mad /= ((double)scores.size()-1.0);
		sd = Math.sqrt(sd);
		
		score_curve.samples.add(new double[]{1,getUpperBound()});
		score_curve.smooth();
	}
	


}
