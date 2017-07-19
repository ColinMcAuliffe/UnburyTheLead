package compare_measures;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.util.Collections;
import java.util.Vector;

import javax.swing.JFrame;
import javax.swing.JPanel;

import compare_measures.measures.*;
import new_metrics.DrawScaled;

import java.io.*;
import java.nio.file.*;

public class Master extends JFrame {
	int size = 1000;
	
	public static double radius = 1.0;
	
	public static int min_districts = 4;

	Vector<iMeasure> all_measures = new Vector<iMeasure>();
	Vector<iMeasure> x_measures = new Vector<iMeasure>();
	Vector<iMeasure> y_measures = new Vector<iMeasure>();
	Vector<Draw> all_draws = new Vector<Draw>();
	
	public DrawPanel panel = null;
	
	public static void main(String[] ss) {
		new Master().show();
	}

	
	public Master() {
		super();
		addAllMeasures();
		addAllDraws();
		scoreAll();
		initComponents();
	}


	public void addAllMeasures() {
		
		int show = 1;
		
		all_measures.add(new MPopularVote());
		all_measures.add(new MSeats());
		all_measures.add(new MNDistricts());
		all_measures.add(new MVoteVariance());
		all_measures.add(new MNagle());
		all_measures.add(new MSpecAsym());
		all_measures.add(new MGrofman());
		all_measures.add(new MMeanMinusMedian());
		all_measures.add(new MEfficiencyGap());
		all_measures.add(new MLopsidedMargins());
		
		switch(show) {
		case 0:
			x_measures.add(new MPopularVote());
			x_measures.add(new MSeats());
			x_measures.add(new MVoteVariance());
			x_measures.add(new MNagle());
			y_measures.add(new MPopularVote());
			y_measures.add(new MSeats());
			y_measures.add(new MVoteVariance());
			y_measures.add(new MNagle());
			break;
		case 1:
			x_measures.add(new MPopularVote());
			x_measures.add(new MSeats());
			x_measures.add(new MVoteVariance());
			x_measures.add(new MNagle());
			y_measures.add(new MSpecAsym());
			y_measures.add(new MGrofman());
			y_measures.add(new MMeanMinusMedian());
			y_measures.add(new MEfficiencyGap());
			y_measures.add(new MLopsidedMargins());
			break;
		case 2:
			x_measures.add(new MNagle());
			x_measures.add(new MSpecAsym());
			x_measures.add(new MGrofman());
			x_measures.add(new MMeanMinusMedian());
			x_measures.add(new MEfficiencyGap());
			x_measures.add(new MLopsidedMargins());
			y_measures.add(new MNagle());
			y_measures.add(new MSpecAsym());
			y_measures.add(new MGrofman());
			y_measures.add(new MMeanMinusMedian());
			y_measures.add(new MEfficiencyGap());
			y_measures.add(new MLopsidedMargins());
			break;
		}

	}
	public void addAllDraws() {
		Vector<String[]> lines = readCSV("congressImputed.csv");
		System.out.println("lines: "+lines.size());
		String last_state = "";
		String last_year = "";

		double total_dem = 0;
		double total_rep = 0;
		Vector<Double> dists = new Vector<Double>();
		Vector<Double> centered_dists = new Vector<Double>();
		boolean header = true;
		for( String[] line : lines) {
			if( header) {
				header = false;
				continue;
			}
			String state = line[1];
			String year = line[2];
			if( !state.equals(last_state) || !year.equals(last_year)) {
				if( dists.size() >= min_districts) {
					Collections.sort(dists);
					Collections.sort(centered_dists);
					
					Draw d = new Draw();
					d.year = Integer.parseInt(last_year);
					d.popular_pct = total_rep/(total_dem+total_rep);
					d.district_pcts = new double[dists.size()];
					for( int i = 0; i < d.district_pcts.length; i++) { d.district_pcts[i] = dists.get(i); } 
					d.centered_district_pcts = new double[centered_dists.size()];
					for( int i = 0; i < d.centered_district_pcts.length; i++) { d.centered_district_pcts[i] = centered_dists.get(i); } 
					all_draws.add(d);
					System.out.println("added draw "+last_state+" "+last_year+" "+d.district_pcts.length+" "+d.popular_pct);
				} else {
					System.out.println("too few districts "+last_state+" "+last_year+" "+dists.size());
				}
				last_state = state;
				last_year = year;
				total_dem = 0;
				total_rep = 0;
				dists = new Vector<Double>();
				centered_dists = new Vector<Double>();
			}
			double d = Double.parseDouble(line[11]);
			double r = Double.parseDouble(line[10]);
			double cd = Double.parseDouble(line[13]);
			double cr = Double.parseDouble(line[12]);
			total_dem += d;
			total_rep += r;
			dists.add(r/(d+r));
			centered_dists.add(cr/(cd+cr));
		}
		
	}
	
	public void scoreAll() {
		for( iMeasure m : all_measures) {
			m.scoreDraws(all_draws);
		}
	}
	
	public void plotAll(DrawScaled g, double x0, double y0, double x1, double y1, double pct_padding, double r) {
		//System.out.println("all_measures.size(): "+all_measures.size());
		double for_labels = 80;
		double xs = x0+for_labels;
		double ys = y0+for_labels;
		
		int count = x_measures.size() > y_measures.size() ? x_measures.size() : y_measures.size();
		double for_each = (x1-xs)/(double)(count);
		double padding = for_each*pct_padding;
		double for_draw = for_each-(padding*2.0);
		//System.out.println("for each: "+for_each);
		g.setColor(Color.black);
		for( int i = 0; i < x_measures.size(); i++) {
			double x = xs+padding+for_each*(double)i;
			iMeasure m1 = x_measures.get(i);

			//draw label
			String s = m1.getAbbr();
			double d = g.stringWidth(s)/2.0;
			double xc = x + (for_each)/2.0 - d;
			System.out.println("label "+s+" "+xc+" "+(y0+for_labels-10));
			g.drawString(s, xc, y0+for_labels-10);
			
			
			for( int j = 0; j < y_measures.size(); j++) {
				double y = ys+padding+for_each*(double)j;
				iMeasure m2 = y_measures.get(j);
				
				if( i == 0) {
					//draw label
					String s2 = m2.getAbbr();
					double d0 = g.stringWidth(s2);
					double xc0 = xs - d0;
					double yc = y + (for_each)/2.0;
					System.out.println("label "+s2+" "+xc0+" "+(yc));
					g.drawString(s2, xc0, yc);
				}
				
				
				g.drawRect((int)x, (int)y, (int)for_draw, (int)for_draw);
				scatterPlot(m1,m2,g,x,x+for_draw,y,y+for_draw,r);
			}
		}
	}
	
	public void scatterPlot(iMeasure m1, iMeasure m2, DrawScaled g, double x0, double x1, double y0, double y1, double r) {
		//System.out.println("scatter plot "+x0+" "+x1+" "+y0+" "+y1);
		for( Draw d : all_draws) {
			double rx = d.scores.get(m1.getAbbr());
			double ry = d.scores.get(m2.getAbbr());
			
			rx = (x1-x0)*(rx-m1.getLowerBound())/(m1.getUpperBound()-m1.getLowerBound())+x0;
			ry = y1-(y1-y0)*(ry-m2.getLowerBound())/(m2.getUpperBound()-m2.getLowerBound());
			g.fillOval((int)(rx-r), (int)(ry-r), (int)(r*2.0), (int)(r*2.0));
			
		}
		
	}
	 
	
	private void initComponents() {
		getContentPane().setLayout(null);
		setSize(size,size);
		setTitle("Draw");
		
		panel = new DrawPanel();
		panel.setBounds(0, 0, 1080, 1080);
		getContentPane().add(panel);
	}
	
	class DrawPanel extends JPanel {
		
	    public void paintComponent(Graphics graphics0) {
	    	try {
	            Graphics2D graphics = (Graphics2D)graphics0;

	            double fsaa=1;
	            Dimension d = this.getSize();
	    		double width = d.getWidth();
	    		double height = d.getHeight();

		        graphics.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_BICUBIC);
		        graphics.setRenderingHint(RenderingHints.KEY_RENDERING,RenderingHints.VALUE_RENDER_QUALITY);
		        graphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
		        graphics.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

			    super.paintComponent(graphics);
			    
			    graphics.setColor(Color.white);
			    graphics.fillRect(0, 0, size, size);
			    width = size;
			    height = size;
			    
			    BufferedImage image = drawOnImage(width*fsaa,height*fsaa,fsaa);
			    //BufferedImage image = drawOnImage(width,height,fsaa);
			    
			    graphics.drawImage(image
			    		,0,0,(int)width,(int)height
			    		//,0,0,(int)width*2,(int)height*2
			    		,null);
	    	} catch (Exception ex) {
	    		ex.printStackTrace();
	    	}
	    }
	}

	public BufferedImage drawOnImage(double _width, double _height, double fsaa) {
		try {

    		BufferedImage off_Image =
	        		  new BufferedImage(
	        				  (int) (_width), 
	        				  (int) (_height), 
	        		          BufferedImage.TYPE_INT_ARGB
	        		          );
	        Graphics2D graphics2 = off_Image.createGraphics();
	        

	        graphics2.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_BICUBIC);
	        graphics2.setRenderingHint(RenderingHints.KEY_RENDERING,RenderingHints.VALUE_RENDER_QUALITY);
	        graphics2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
	        graphics2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
	        graphics2.setStroke(new BasicStroke((int)fsaa));
	        graphics2.setFont(new Font("Arial",0,20));
	        
	        DrawScaled graphics = new DrawScaled(graphics2,_width/1000.0,_height/1000.0,fsaa);
	        graphics.setColor(Color.white);
	        graphics.fillRect(0, 0, (int)_width, (int)_height);

	        
	        plotAll(graphics, 0, 0, (int)_width, (int)_height, 0.03, radius); 
	        
	        return off_Image;
		} catch (Exception ex) {
			ex.printStackTrace();
			return null;
		}
	}
	
	
	public Vector<String[]> readCSV(String filename) {
		Vector<String[]> vss = new Vector<String[]>();
		
		try {
			String content = new String(Files.readAllBytes(Paths.get(filename)));
			String[] lines = content.split("\n");
			for( String line : lines) {
		        String[] tokens = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);
		        vss.add(tokens);
		        for(String t : tokens) {
		            //System.out.print("["+t+"]");
		        }
		        //System.out.println();
			}
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		
		return vss;
	}
		
	

}
