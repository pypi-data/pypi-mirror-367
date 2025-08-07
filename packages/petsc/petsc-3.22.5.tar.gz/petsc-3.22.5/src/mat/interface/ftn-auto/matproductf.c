#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matproduct.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductreplacemats_ MATPRODUCTREPLACEMATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductreplacemats_ matproductreplacemats
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductsetfromoptions_ MATPRODUCTSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductsetfromoptions_ matproductsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductview_ MATPRODUCTVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductview_ matproductview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductnumeric_ MATPRODUCTNUMERIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductnumeric_ matproductnumeric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductsymbolic_ MATPRODUCTSYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductsymbolic_ matproductsymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductsetfill_ MATPRODUCTSETFILL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductsetfill_ matproductsetfill
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductsetalgorithm_ MATPRODUCTSETALGORITHM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductsetalgorithm_ matproductsetalgorithm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductgetalgorithm_ MATPRODUCTGETALGORITHM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductgetalgorithm_ matproductgetalgorithm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductsettype_ MATPRODUCTSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductsettype_ matproductsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductclear_ MATPRODUCTCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductclear_ matproductclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductcreatewithmat_ MATPRODUCTCREATEWITHMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductcreatewithmat_ matproductcreatewithmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductcreate_ MATPRODUCTCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductcreate_ matproductcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductgettype_ MATPRODUCTGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductgettype_ matproductgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matproductgetmats_ MATPRODUCTGETMATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matproductgetmats_ matproductgetmats
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matproductreplacemats_(Mat A,Mat B,Mat C,Mat D, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(C);
CHKFORTRANNULLOBJECT(D);
*ierr = MatProductReplaceMats(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((C) ),
	(Mat)PetscToPointer((D) ));
}
PETSC_EXTERN void  matproductsetfromoptions_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductSetFromOptions(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matproductview_(Mat mat,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatProductView(
	(Mat)PetscToPointer((mat) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matproductnumeric_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductNumeric(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matproductsymbolic_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductSymbolic(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matproductsetfill_(Mat mat,PetscReal *fill, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductSetFill(
	(Mat)PetscToPointer((mat) ),*fill);
}
PETSC_EXTERN void  matproductsetalgorithm_(Mat mat,char *alg, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for alg */
  FIXCHAR(alg,cl0,_cltmp0);
*ierr = MatProductSetAlgorithm(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(alg,_cltmp0);
}
PETSC_EXTERN void  matproductgetalgorithm_(Mat mat,char *alg, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductGetAlgorithm(
	(Mat)PetscToPointer((mat) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for alg */
*ierr = PetscStrncpy(alg, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, alg, cl0);
}
PETSC_EXTERN void  matproductsettype_(Mat mat,MatProductType *productype, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductSetType(
	(Mat)PetscToPointer((mat) ),*productype);
}
PETSC_EXTERN void  matproductclear_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductClear(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matproductcreatewithmat_(Mat A,Mat B,Mat C,Mat D, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(C);
CHKFORTRANNULLOBJECT(D);
*ierr = MatProductCreateWithMat(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((C) ),
	(Mat)PetscToPointer((D) ));
}
PETSC_EXTERN void  matproductcreate_(Mat A,Mat B,Mat C,Mat *D, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(C);
PetscBool D_null = !*(void**) D ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(D);
*ierr = MatProductCreate(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((C) ),D);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! D_null && !*(void**) D) * (void **) D = (void *)-2;
}
PETSC_EXTERN void  matproductgettype_(Mat mat,MatProductType *mtype, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatProductGetType(
	(Mat)PetscToPointer((mat) ),mtype);
}
PETSC_EXTERN void  matproductgetmats_(Mat mat,Mat *A,Mat *B,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatProductGetMats(
	(Mat)PetscToPointer((mat) ),A,B,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
