package corgis.school_scores.domain;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import corgis.school_scores.domain.Male;
import corgis.school_scores.domain.Female;

/**
 * 
 */
public class Gender {
	
    private Male male;
    private Female female;
    
    
    /*
     * @return 
     */
    public Male getMale() {
        return this.male;
    }
    
    
    
    /*
     * @return 
     */
    public Female getFemale() {
        return this.female;
    }
    
    
    
	
	/**
	 * Creates a string based representation of this Gender.
	
	 * @return String
	 */
	public String toString() {
		return "Gender[" +male+", "+female+"]";
	}
	
	/**
	 * Internal constructor to create a Gender from a  representation.
	 * @param json_data The raw json data that will be parsed.
	 */
    public Gender(JSONObject json_data) {
        try {// Male
            this.male = new Male((JSONObject)json_data.get("Male"));// Female
            this.female = new Female((JSONObject)json_data.get("Female"));
        } catch (NullPointerException e) {
    		System.err.println("Could not convert the response to a Gender; a field was missing.");
    		e.printStackTrace();
    	} catch (ClassCastException e) {
    		System.err.println("Could not convert the response to a Gender; a field had the wrong structure.");
    		e.printStackTrace();
        }
	}	
}