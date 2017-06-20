package serialization;
public interface iJSONObject{
	public JSONObject instantiateObject(String key);
	public void post_deserialize();
	public void pre_serialize();
}