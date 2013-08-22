import java.io.UnsupportedEncodingException;
import java.security.SecureRandom;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class Encryptor {
    /*
	public static String password = "qweeee";
	
    public Encrypt(String password) {
		super();
		this.password = password;
	}
    */
	/** 
     * 加密 
     *  
     * @param content 需要加密的内容 
     * @param password  加密密码 
     * @return 
     */  
    public static byte[] encrypt(String content, String password) {  
            try {             
            	
                    KeyGenerator kgen = KeyGenerator.getInstance("AES"); //AES密钥生成器
                    //128是密钥的长度  SecureRandom是随机生成数  但是我们需要摄入确定的值
                    SecureRandom random=SecureRandom.getInstance("SHA1PRNG");//需要自己手动设置   
                    random.setSeed(password.getBytes());   
                    kgen.init(128, random);//初始化密钥
                    SecretKey secretKey = kgen.generateKey(); //分组秘密密钥（并为其提供类型安全）
                    byte[] enCodeFormat = secretKey.getEncoded();  
                    SecretKeySpec key = new SecretKeySpec(enCodeFormat, "AES"); //对产生的密钥再进行封装 
                    Cipher cipher = Cipher.getInstance("AES");// 创建密码器   
                    byte[] byteContent = content.getBytes("utf-8");  //获得原文utf-8编码格式的字节数
                    cipher.init(Cipher.ENCRYPT_MODE, key);// 加密初始化   Cipher.ENCRYPT_MODE为加密
                    byte[] result = cipher.doFinal(byteContent);  //密码器执行加密 并生成加密字节数组
                    return result; // 加密   
            } catch (Exception e) {  
                    //e.printStackTrace();  
            } 
            return null;  
    }  
    /**解密 
     * @param content  待解密内容 
     * @param password 解密密钥 
     * @return 
     */  
    public static String decrypt(byte[] content, String password) {  
            try {  
                     KeyGenerator kgen = KeyGenerator.getInstance("AES");  //AES密钥生成器
                     //128是密钥的长度  SecureRandom是随机生成数  但是我们需要摄入确定的值
                     SecureRandom random=SecureRandom.getInstance("SHA1PRNG");//需要自己手动设置   
                     random.setSeed(password.getBytes());   
                     kgen.init(128, random);//初始化密钥
                     SecretKey secretKey = kgen.generateKey();  //分组秘密密钥（并为其提供类型安全）
                     byte[] enCodeFormat = secretKey.getEncoded();  
                     SecretKeySpec key = new SecretKeySpec(enCodeFormat, "AES");  //对产生的密钥再进行封装             
                     Cipher cipher = Cipher.getInstance("AES");// 创建密码器   
                    cipher.init(Cipher.DECRYPT_MODE, key);// 解密初始化   Cipher.DECRYPT_MODE为解密
                    byte[] result = cipher.doFinal(content);  //密码器执行解密密 并生成解密密字节数组
                    return new String(result); // 解密   
            } catch (Exception e) {  
                    //e.printStackTrace();  
            } 
            return null;  
    }  
    
    //将2进制转移成16进制
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
    
    ////将16进制转移成2进制
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
    	
     /**
	 * soap加密接口   
	 * @param content xml明文
	 * @param password 密码
	 * @return 16进制密文
	 */
	public static String get_encrypt_by_password(String content, String password){
		return parseByte2HexStr(encrypt(content, password));
	}
     
     /**
	 * soap解密接口   
	 * @param hexStr 加密后的xml文本
	 * @param password 密码
	 * @return 明文
	 */
	public static String get_decrypt_by_password(String hexStr, String password){
		return decrypt(parseHexStr2Byte(hexStr), password);
	}
    
    public static void main(String args[]) throws UnsupportedEncodingException {
        try {
			String function = args[0].toString();
			String inputStr = args[1].toString();
			String password = args[2].toString();
			if (function.equals("-encrypt") || function.equals("-decrypt")) {
				if (function.equals("-encrypt")) {
					String result = get_encrypt_by_password(inputStr, password);
                                        if (result == null) {
                                                System.out.println("Wrong input string to encrypt ");
                                        } else {
                                                System.out.println(result);
                                        }
				}
				if (function.equals("-decrypt")) {
					String result = get_decrypt_by_password(inputStr, password);
					if (result == null) {
						System.out.println("Wrong input string to be decrypted");
					} else {
						System.out.println(result);
					}
				}
			} else {
				show_function();
			}
		} catch (Exception e) {
			show_function();
		}
    }

    public static void show_function() {
		System.out.println("-encrypt <string to encrypt>");
		System.out.println("-decrypt <string to decrypt>");
	}
    

}
