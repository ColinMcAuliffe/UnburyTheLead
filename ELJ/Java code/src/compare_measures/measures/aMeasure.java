package compare_measures.measures;

import java.util.Collections;
import java.util.Vector;

import util.Pair;

import compare_measures.Draw;
import compare_measures.IntegrationFunction;

public abstract class aMeasure implements iMeasure, IntegrationFunction {
	
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
	
	
	@Override
	public void scoreDraws(Vector<Draw> draws) {
		Vector<Pair<Double,Draw>> scores = new Vector<Pair<Double,Draw>>(); 
		for( Draw draw : draws) {
			scores.add(new Pair(getScore(draw),draw));
		}
		Collections.sort(scores);
		
		double inc = 1.0/(double)scores.size();
		double cur = inc/2.0;
		score_curve.samples.add(new double[]{0,getLowerBound()});
		for( int i = 0; i < scores.size(); i++) {
			Pair<Double,Draw> score = scores.get(i);
			score.b.scores.put(getAbbr(), score.a);
			score.b.scores.put(getAbbr()+" percentile", cur);
			score_curve.samples.add(new double[]{cur,score.a});
			cur += inc;
		}
		score_curve.samples.add(new double[]{1,getUpperBound()});
		score_curve.smooth();
	}
	

}
