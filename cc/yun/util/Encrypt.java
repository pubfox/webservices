package openstack_dashboard_webservices.cc.yun.util;

import java.io.UnsupportedEncodingException;
import java.security.SecureRandom;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class Encrypt {
	public static String password = "qweeee";
	
    public Encrypt(String password) {
		super();
		this.password = password;
	}
    public static byte[] encrypt(String content, String password) {  
            try {             
                    KeyGenerator kgen = KeyGenerator.getInstance("AES");  
                    kgen.init(128, new SecureRandom(password.getBytes()));  
                    SecretKey secretKey = kgen.generateKey();  
                    byte[] enCodeFormat = secretKey.getEncoded();  
                    SecretKeySpec key = new SecretKeySpec(enCodeFormat, "AES");  
                    Cipher cipher = Cipher.getInstance("AES");
                    byte[] byteContent = content.getBytes("utf-8");  
                    cipher.init(Cipher.ENCRYPT_MODE, key);
                    byte[] result = cipher.doFinal(byteContent);  
                    return result; 
            } catch (Exception e) {  
                    e.printStackTrace();  
            } 
            return null;  
    }  
    public static String decrypt(byte[] content, String password) {  
            try {  
                     KeyGenerator kgen = KeyGenerator.getInstance("AES");  
                     kgen.init(128, new SecureRandom(password.getBytes()));  
                     SecretKey secretKey = kgen.generateKey();  
                     byte[] enCodeFormat = secretKey.getEncoded();  
                     SecretKeySpec key = new SecretKeySpec(enCodeFormat, "AES");              
                     Cipher cipher = Cipher.getInstance("AES");
                    cipher.init(Cipher.DECRYPT_MODE, key);
                    byte[] result = cipher.doFinal(content);  
                    return new String(result);
            } catch (Exception e) { 
                    e.printStackTrace();  
            } 
            return null;  
    }  
    
    public static String parseByte2HexStr(byte buf[]){
    	StringBuffer sb=new StringBuffer();
    	for(int i=0;i<buf.length;i++){
    		String hex=Integer.toHexString(buf[i]&0xFF);
    		if(hex.length()==1){
    			hex='0' + hex;
    		}
    		sb.append(hex.toUpperCase());
    		}
    	return sb.toString();
    }
    
    public static byte[] parseHexStr2Byte(String hexStr){
    	if(hexStr.length()<1)
    		return null;
    	byte[]result=new byte[hexStr.length()/2];
    	for(int i=0;i<hexStr.length()/2;i++){
    		int high=Integer.parseInt(hexStr.substring(i*2,i*2+1),16);
    		int low=Integer.parseInt(hexStr.substring(i*2+1,i*2+2),16);
    		result[i]=(byte)(high*16+low);
    		}
    	return result;
    	}

    public static String get_decrypt_by_password(String hexStr, String password){
        return decrypt(parseHexStr2Byte(hexStr), password);
    }
     
    public static void main(String args[]) throws UnsupportedEncodingException {
        System.out.println(parseByte2HexStr(encrypt("123edsss", "qweeee")));
    }
    

}
