package corgis.supreme_court.domain;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;


/**
 * 
 */
public class Source {
	
    private String state;
    private Integer id;
    private String name;
    
    
    /*
     * @return 
     */
    public String getState() {
        return this.state;
    }
    
    
    
    /*
     * @return 
     */
    public Integer getId() {
        return this.id;
    }
    
    
    
    /*
     * @return 
     */
    public String getName() {
        return this.name;
    }
    
    
    
	
	/**
	 * Creates a string based representation of this Source.
	
	 * @return String
	 */
	public String toString() {
		return "Source[" +state+", "+id+", "+name+"]";
	}
	
	/**
	 * Internal constructor to create a Source from a  representation.
	 * @param json_data The raw json data that will be parsed.
	 */
    public Source(JSONObject json_data) {
        try {// state
            this.state = (String)json_data.get("state");// id
            this.id = new Integer(((Long)json_data.get("id")).intValue());// name
            this.name = (String)json_data.get("name");
        } catch (NullPointerException e) {
    		System.err.println("Could not convert the response to a Source; a field was missing.");
    		e.printStackTrace();
    	} catch (ClassCastException e) {
    		System.err.println("Could not convert the response to a Source; a field had the wrong structure.");
    		e.printStackTrace();
        }
	}	
}