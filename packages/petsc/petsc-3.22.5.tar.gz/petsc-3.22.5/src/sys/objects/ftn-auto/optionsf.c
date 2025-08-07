#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* options.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionscreate_ PETSCOPTIONSCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionscreate_ petscoptionscreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsdestroy_ PETSCOPTIONSDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsdestroy_ petscoptionsdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionspush_ PETSCOPTIONSPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionspush_ petscoptionspush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionspop_ PETSCOPTIONSPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionspop_ petscoptionspop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsvalidkey_ PETSCOPTIONSVALIDKEY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsvalidkey_ petscoptionsvalidkey
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsinsertstring_ PETSCOPTIONSINSERTSTRING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsinsertstring_ petscoptionsinsertstring
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsinsertfile_ PETSCOPTIONSINSERTFILE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsinsertfile_ petscoptionsinsertfile
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsview_ PETSCOPTIONSVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsview_ petscoptionsview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsprefixpush_ PETSCOPTIONSPREFIXPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsprefixpush_ petscoptionsprefixpush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsprefixpop_ PETSCOPTIONSPREFIXPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsprefixpop_ petscoptionsprefixpop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsclear_ PETSCOPTIONSCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsclear_ petscoptionsclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionssetalias_ PETSCOPTIONSSETALIAS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionssetalias_ petscoptionssetalias
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionssetvalue_ PETSCOPTIONSSETVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionssetvalue_ petscoptionssetvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsclearvalue_ PETSCOPTIONSCLEARVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsclearvalue_ petscoptionsclearvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsreject_ PETSCOPTIONSREJECT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsreject_ petscoptionsreject
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionshashelp_ PETSCOPTIONSHASHELP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionshashelp_ petscoptionshashelp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionshasname_ PETSCOPTIONSHASNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionshasname_ petscoptionshasname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsused_ PETSCOPTIONSUSED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsused_ petscoptionsused
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsallused_ PETSCOPTIONSALLUSED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsallused_ petscoptionsallused
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsleft_ PETSCOPTIONSLEFT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsleft_ petscoptionsleft
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscoptionscreate_(PetscOptions *options, int *ierr)
{
PetscBool options_null = !*(void**) options ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(options);
*ierr = PetscOptionsCreate(options);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! options_null && !*(void**) options) * (void **) options = (void *)-2;
}
PETSC_EXTERN void  petscoptionsdestroy_(PetscOptions *options, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(options);
 PetscBool options_null = !*(void**) options ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(options);
*ierr = PetscOptionsDestroy(options);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! options_null && !*(void**) options) * (void **) options = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(options);
 }
PETSC_EXTERN void  petscoptionspush_(PetscOptions opt, int *ierr)
{
CHKFORTRANNULLOBJECT(opt);
*ierr = PetscOptionsPush(
	(PetscOptions)PetscToPointer((opt) ));
}
PETSC_EXTERN void  petscoptionspop_(int *ierr)
{
*ierr = PetscOptionsPop();
}
PETSC_EXTERN void  petscoptionsvalidkey_( char key[],PetscBool *valid, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for key */
  FIXCHAR(key,cl0,_cltmp0);
*ierr = PetscOptionsValidKey(_cltmp0,valid);
  FREECHAR(key,_cltmp0);
}
PETSC_EXTERN void  petscoptionsinsertstring_(PetscOptions options, char in_str[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for in_str */
  FIXCHAR(in_str,cl0,_cltmp0);
*ierr = PetscOptionsInsertString(
	(PetscOptions)PetscToPointer((options) ),_cltmp0);
  FREECHAR(in_str,_cltmp0);
}
PETSC_EXTERN void  petscoptionsinsertfile_(MPI_Fint * comm,PetscOptions options, char file[],PetscBool *require, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for file */
  FIXCHAR(file,cl0,_cltmp0);
*ierr = PetscOptionsInsertFile(
	MPI_Comm_f2c(*(comm)),
	(PetscOptions)PetscToPointer((options) ),_cltmp0,*require);
  FREECHAR(file,_cltmp0);
}
PETSC_EXTERN void  petscoptionsview_(PetscOptions options,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscOptionsView(
	(PetscOptions)PetscToPointer((options) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscoptionsprefixpush_(PetscOptions options, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscOptionsPrefixPush(
	(PetscOptions)PetscToPointer((options) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscoptionsprefixpop_(PetscOptions options, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
*ierr = PetscOptionsPrefixPop(
	(PetscOptions)PetscToPointer((options) ));
}
PETSC_EXTERN void  petscoptionsclear_(PetscOptions options, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
*ierr = PetscOptionsClear(
	(PetscOptions)PetscToPointer((options) ));
}
PETSC_EXTERN void  petscoptionssetalias_(PetscOptions options, char newname[], char oldname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for newname */
  FIXCHAR(newname,cl0,_cltmp0);
/* insert Fortran-to-C conversion for oldname */
  FIXCHAR(oldname,cl1,_cltmp1);
*ierr = PetscOptionsSetAlias(
	(PetscOptions)PetscToPointer((options) ),_cltmp0,_cltmp1);
  FREECHAR(newname,_cltmp0);
  FREECHAR(oldname,_cltmp1);
}
PETSC_EXTERN void  petscoptionssetvalue_(PetscOptions options, char name[], char value[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
/* insert Fortran-to-C conversion for value */
  FIXCHAR(value,cl1,_cltmp1);
*ierr = PetscOptionsSetValue(
	(PetscOptions)PetscToPointer((options) ),_cltmp0,_cltmp1);
  FREECHAR(name,_cltmp0);
  FREECHAR(value,_cltmp1);
}
PETSC_EXTERN void  petscoptionsclearvalue_(PetscOptions options, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscOptionsClearValue(
	(PetscOptions)PetscToPointer((options) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscoptionsreject_(PetscOptions options, char pre[], char name[], char mess[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1, PETSC_FORTRAN_CHARLEN_T cl2)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
  char *_cltmp2 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for pre */
  FIXCHAR(pre,cl0,_cltmp0);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl1,_cltmp1);
/* insert Fortran-to-C conversion for mess */
  FIXCHAR(mess,cl2,_cltmp2);
*ierr = PetscOptionsReject(
	(PetscOptions)PetscToPointer((options) ),_cltmp0,_cltmp1,_cltmp2);
  FREECHAR(pre,_cltmp0);
  FREECHAR(name,_cltmp1);
  FREECHAR(mess,_cltmp2);
}
PETSC_EXTERN void  petscoptionshashelp_(PetscOptions options,PetscBool *set, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
*ierr = PetscOptionsHasHelp(
	(PetscOptions)PetscToPointer((options) ),set);
}
PETSC_EXTERN void  petscoptionshasname_(PetscOptions options, char pre[], char name[],PetscBool *set, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for pre */
  FIXCHAR(pre,cl0,_cltmp0);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl1,_cltmp1);
*ierr = PetscOptionsHasName(
	(PetscOptions)PetscToPointer((options) ),_cltmp0,_cltmp1,set);
  FREECHAR(pre,_cltmp0);
  FREECHAR(name,_cltmp1);
}
PETSC_EXTERN void  petscoptionsused_(PetscOptions options, char *name,PetscBool *used, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscOptionsUsed(
	(PetscOptions)PetscToPointer((options) ),_cltmp0,used);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscoptionsallused_(PetscOptions options,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
CHKFORTRANNULLINTEGER(N);
*ierr = PetscOptionsAllUsed(
	(PetscOptions)PetscToPointer((options) ),N);
}
PETSC_EXTERN void  petscoptionsleft_(PetscOptions options, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
*ierr = PetscOptionsLeft(
	(PetscOptions)PetscToPointer((options) ));
}
#if defined(__cplusplus)
}
#endif
