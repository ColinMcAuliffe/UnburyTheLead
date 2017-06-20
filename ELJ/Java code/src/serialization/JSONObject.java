package serialization;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Stack;
import java.util.Vector;

//this class is for parsing a json string into an object, and formatting an object into a json string.
//objects that you want to be able to save and load from/to a file should extend this object and implement the methods in iJSONObject.
//loading from a file will create key-value pairs in the hashmap it extends.  saving will create a json string from same.
//hence, move all data to it via pre_serialize before you save, and from it via post_deserialize after you load.
//that's it!
//check out the "jsonObjects" package for examples.
//note: this is a single-pass in-place serializer / de-serializer!   that is, all work, including object instantiation and member initialization, is done in one pass!
public abstract class JSONObject extends HashMap<String, Object> implements iJSONObject{
	public static int _json_verbosity = 0;
	private static final String _json_quote = "\"";
	private static final String _json_tab = "  ";
	private static final long serialVersionUID = 1L;
	public boolean _json_add_comma = false;
	public int deserialize(String s, int index){
		if(index < 0){
			index = 0;
		}
		String key = null;
		int mode = 0;
		int last_index = index;
		Stack<Vector<Object>> svo = new Stack<>();
		// Vector v = null;
		int array = 0;
		JSONObject o = null;
		while(index < s.length()){
			char c = s.charAt(index);
			if(JSONObject._json_verbosity > 0){
				//System.out.print(c);
			}
			switch(c){
			case '{':
				// ignore if no key encountered yet.
				if((key == null) || (key.length() == 0)){
					index++;
					last_index = index;
				}
				else{
					o = instantiateObject(key);
					index = o.deserialize(s, ++index);
				}
				break;
			case '}':
				if(mode == 1){
					if(array == 2){
						array = 0;
						mode = 0;
						put(key, svo.pop());
						if(JSONObject._json_verbosity > 0){
							//System.out.println("|putting array " + key + " " + "| " + size());
						}
						last_index = index + 1;
					}
					else{
						mode = 0;
						if(o != null){
							put(key, o);
							if(JSONObject._json_verbosity > 0){
								//System.out.println("|putting " + key + " object| " + size());
							}
							o = null;
						}
						else{
							String ss = s.substring(last_index, index).replaceAll("\"", "").trim();
							put(key, ss);
							if(JSONObject._json_verbosity > 0){
								//System.out.println("|putting " + key + " " + ss + "| " + size());
							}
						}
						last_index = index + 1;
					}
				}
				post_deserialize();
				return index;
			case '"':
				if(JSONObject._json_verbosity > 1){
					//System.out.println("skipping quotes");
				}
				index++;
				for(; index < s.length(); index++){
					char c2 = s.charAt(index);
					if(c2 == '"'){
						break;
					}
				}
				break;
			case ',':
				if(mode == 0){
					break;
				}
				if(array == 1){
					if(o != null){
						svo.peek().add(o);
						o = null;
					}
					else{
						svo.peek().add(s.substring(last_index, index).replaceAll("\"", "").trim());
					}
					last_index = index + 1;
				}
				else if(array == 2){
					array = 0;
					mode = 0;
					if(JSONObject._json_verbosity > 0){
						//System.out.println("|putting array3 " + key + " " + "|");
					}
					put(key, svo.pop());
					last_index = index + 1;
				}
				else{
					mode = 0;
					if(o != null){
						put(key, o);
						if(JSONObject._json_verbosity > 0){
							//System.out.println("|putting1 " + key + " object| " + size());
						}
						o = null;
					}
					else{
						String ss = s.substring(last_index, index).replaceAll("\"", "").trim();
						put(key, ss);
						if(JSONObject._json_verbosity > 0){
							///System.out.println("|putting2 " + key + " " + ss + "| " + size());
						}
					}
					last_index = index + 1;
				}
				break;
			case ':':
				key = s.substring(last_index, index).replaceAll("\"", "").replaceAll("\\,", "").trim();
				mode = 1;
				last_index = index + 1;
				break;
			case '[':
				svo.push(new Vector<>());
				last_index = index + 1;
				array = 1;
				break;
			case ']':
				if((array == 1) && ((last_index + 1) < index)){
					if(o != null){
						svo.peek().add(o);
						o = null;
					}
					else{
						String s2 = s.substring(last_index, index).replaceAll("\"", "").trim();
						if(s2.length() > 0){
							svo.peek().add(s2);
						}
					}
				}
				array = 2;
				if(JSONObject._json_verbosity > 0){
					//System.out.println("|putting array2 " + key + " " + svo.size() + " " + svo.peek().size() + " \"" + svo.peek() + "\"|");
				}
				Vector<Object> v = svo.pop();
				if(svo.size() > 0){
					svo.peek().add(v);
					// v = svo.pop();
					array = 1;
				}
				else{
					put(key, v);
					mode = 0;
					array = 0;
					v = null;
				}
				last_index = index + 1;
				break;
			default:
			}
			index++;
		}
		if(mode != 0){
			if((array == 1) && (svo.size() > 0)){
				if(o != null){
					svo.peek().add(o);
					o = null;
				}
				else{
					svo.peek().add(s.substring(last_index, index).replaceAll("\"", "").trim());
				}
				Vector<Object> v = svo.pop();
				while(svo.size() > 0){
					svo.peek().add(v);
					v = svo.pop();
				}
				// this.put(key, v);
				last_index = index + 1;
			}
			else if(array == 2){
				array = 0;
				mode = 0;
				if(JSONObject._json_verbosity > 0){
					//System.out.println("|putting array3 " + key + " " + svo.size() + " " + svo.peek().size() + " " + svo.peek() + "|");
				}
				Vector<Object> v = svo.pop();
				while(svo.size() > 0){
					svo.peek().add(v);
					v = svo.pop();
				}
				put(key, v);
				last_index = index + 1;
			}
			else{
				mode = 0;
				if(o != null){
					put(key, o);
					if(JSONObject._json_verbosity > 0){
						//System.out.println("|putting1 " + key + " object| " + size());
					}
					o = null;
				}
				else{
					if(index > s.length()){
						index = s.length();
					}
					if(last_index <= s.length()){
						String ss = s.substring(last_index, index).replaceAll("\"", "").trim();
						put(key, ss);
						if(JSONObject._json_verbosity > 0){
							//System.out.println("|putting2 " + key + " " + ss + "| " + size());
						}
					}
				}
				last_index = index + 1;
			}
		}
		post_deserialize();
		return index;
	}
	public JSONObject fromJSON(String s){
		deserialize(s, 0);
		return this;
	}
	public double getDouble(String key){
		if(!containsKey(key)){
			return 0;
		}
		return new Double((String) get(key));
	}
	public JSONObject getObject(String key){
		return (JSONObject) get(key);
	}
	public String getString(String key){
		return get(key).toString();
	}
	public Vector getVector(String key){
		return (Vector) get(key);
	}
	public void serialize(StringBuffer sb, String prepend){
		pre_serialize();
		_json_add_comma = false;
		// sb.append(prepend+"{\n");
		for(Map.Entry<String, Object> t : entrySet()){
			writeObject(t.getKey(), t.getValue(), sb, prepend + JSONObject._json_tab, _json_add_comma);
			_json_add_comma = true;
		}
		// sb.append(prepend+"},\n");
	}
	public String toJSON(){
		StringBuffer sb = new StringBuffer();
		serialize(sb, "");
		return sb.toString();
	}
	private void writeObject(String name, Object obj, StringBuffer sb, String _prepend, boolean comma){
		if(name != null){
			sb.append(_prepend + (comma ? "," : "") + JSONObject._json_quote + name + JSONObject._json_quote + ":");
		}
		if(obj instanceof JSONObject){
			JSONObject o = (JSONObject) obj;
			o.pre_serialize();
			if(name == null){
				sb.append(_prepend + (comma ? "," : ""));
			}
			sb.append("{\n");
			o.serialize(sb, _prepend + JSONObject._json_tab);
			sb.append(_prepend + "}\n");
		}
		else{
			if(obj instanceof Collection){
				sb.append("[\n");
				boolean acomma = false;
				for(Object o : (Collection<Object>) obj){
					writeObject(null, o, sb, _prepend + JSONObject._json_tab, acomma);
					acomma = true;
				}
				sb.append(_prepend + "]\n");
			}
			else if(obj instanceof String){
				sb.append(JSONObject._json_quote + ((String) obj) + JSONObject._json_quote + "\n");
			}
			else if(obj instanceof Integer){
				sb.append(((Integer) obj).intValue() + "\n");
			}
			else if(obj instanceof Float){
				sb.append(((Float) obj).doubleValue() + "\n");
			}
			else{
				sb.append(obj + "\n");
			}
		}
	}
}