package serialization;
public class DefaultJSONObject extends JSONObject{
	private static final long serialVersionUID = 1L;
	public DefaultJSONObject(){
		super();
	}
	public DefaultJSONObject(String from){
		this();
		fromJSON(from);
	}
	@Override
	public JSONObject instantiateObject(String key){
		return new DefaultJSONObject();
	}
	@Override
	public void post_deserialize(){}
	@Override
	public void pre_serialize(){}
}