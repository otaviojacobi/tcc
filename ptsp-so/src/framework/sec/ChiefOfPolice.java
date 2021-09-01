package framework.sec;

import java.io.FilePermission;
import java.lang.reflect.ReflectPermission;
import java.net.NetPermission;
import java.security.Permission;
import java.security.SecurityPermission;
import java.util.PropertyPermission;
import java.util.PropertyResourceBundle;

//ChiefPolice.start();//initiate security
public final class ChiefOfPolice extends SecurityManager 
{
    private static ChiefOfPolice instance;
    private static String[] allowedRead={	".*.class", ".*.txt", ".*.xml", ".*random", ".*jdom.jar", ".*xercesImpl.jar",
            ".*jaxp.properties", ".*SAXParserFactory", ".*resources.jar", ".*SAXMessages_en.properties*", ".*SAXMessages_en_GB.properties",
            ".*meta-index", ".*rt.jar", ".*sunrsasign.jar", ".*jsse.jar", ".*jce.jar", ".*charsets.jar", ".*jre/classes"};    	//any class in controller's directory
    private static String[] allowedWrite={	".*controllers.*txt",		//text files in controller's directory
											".*controllers.*xml"};		//xml files in controller's directory
    private static String[] allowedSec={	"getProperty.securerandom.source", "putProviderProperty.SUN"};
    private static String[] allowedRuntime={"accessClassInPackage.sun.reflect", "reflectionFactoryAccess", "accessDeclaredMembers",
                                            "createClassLoader"};

    public static void start() 
    {
        if(instance!=null) 
        {
            throw new SecurityException("Security Manager already exists");
        }

        instance=new ChiefOfPolice();
        System.setSecurityManager(instance);
    }

    private ChiefOfPolice(){}

    public void checkPermission(Permission permission,Object context) 
    {
        checkPermission(permission);
    }

	private boolean containsRead(String perm)
    {
    	for(int i=0;i<allowedRead.length;i++)
    		if(perm.matches(allowedRead[i]))
    			return true;
    	
    	return false;
    }
    
    private boolean containsWrite(String perm)
    {
    	for(int i=0;i<allowedWrite.length;i++)
    		if(perm.matches(allowedWrite[i]))
    			return true;
    	
    	return false;
    }

    private boolean containsSec(String perm)
    {
        for(int i=0;i<allowedSec.length;i++)
            if(perm.matches(allowedSec[i]))
                return true;

        return false;
    }

    private boolean containsRunime(String perm)
    {
        for(int i=0;i<allowedRuntime.length;i++)
            if(perm.matches(allowedRuntime[i]))
                return true;

        return false;
    }
    
    public void checkPermission(Permission permission) 
    {
        Class<?>[] classes=getClassContext();

        for(int i=0;i<classes.length;i++)
        {
        	if(classes[i].toString().matches(".*controllers.*"))// || classes[i].toString().matches(".*\\.MyGhosts"))
        	{        	
        		if(permission instanceof FilePermission)
        		{
          			if(permission.getActions().endsWith("read") && containsRead(permission.getName()))
        				return;
          			else if(permission.getActions().endsWith("write") && containsWrite(permission.getName()))
        				return;        			
        			else
        			{
        				throw new SecurityException("Security breach 1: name: " + ((FilePermission)permission).getName()
                                + " " + ((FilePermission)permission).getActions());
        			}
        		}else if(permission instanceof PropertyPermission)
                {
                    return;
                }
                else if(permission instanceof SecurityPermission)
                {
                    if(containsSec(permission.getName()))
                    {
                        return;
                    }

                } else if(permission instanceof ReflectPermission)
                {
                    if(permission.getName().equals("suppressAccessChecks"))
                    {
                        return;
                    }

                } else if(permission instanceof RuntimePermission)
                {
                    if( containsRunime(permission.getName()) )
                    {
                        return;
                    }
                } else if(permission instanceof NetPermission)
                {
                    //if( containsRunime(permission.getName()) )
                    if(permission.getName().equals("specifyStreamHandler"))
                    {
                        return;
                    }
                }

        		throw new SecurityException("Security breach 2: " + permission.toString() + " " + permission.getName());
        	}
        }
    }
}