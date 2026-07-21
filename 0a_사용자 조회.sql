declare @fact  char(2),
        @idno  varchar(20),
		@pasw  varchar(20),
		@count int

SET @fact = 'Y6'
SET @idno = 'Y6'
SET @pasw = 'q'

SELECT @count = count(*)
  FROM bauser
 WHERE user_fact = @fact and
       user_idno = @idno and
	   user_pasw = @pasw

SET @count = isnull(@count,0)

IF @count > 0
   BEGIN
     SELECT 'Connect OK!'
   END

IF @count = 0
   BEGIN
     SELECT 'Invaild ID & Psw'
   END